# MCTS

import logging
import math
from typing import Tuple

import numpy as np
from agents.adversarial.puppets import Puppet

from core.game import GameManager
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam, AttackResponse, PassFigure, Wait, MoveLoadInto
from core.const import RED, BLUE

from agents import MatchManager
from agents.reinforced.nn import ModelWrapper
from core.game.board import GameBoard
from core.game.state import GameState
from utils.copy import deepcopy

logger = logging.getLogger(__name__)

EPS = 1e-8

ACT: str = 'Action'
RES: str = 'Response'

WEAPONS_INDICES: dict = {
    'AT': 0,
    'AR': 1,
    'CA': 2,
    'MT': 3,
    'GR': 4,
    'MG': 5,
    'SG': 6,
    'SR': 7
}


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, nnet_RED_Act: ModelWrapper, nnet_RED_Res: ModelWrapper, nnet_BLUE_Act: ModelWrapper, nnet_BLUE_Res: ModelWrapper,
                 seed: int, max_weapon_per_figure: int, max_figure_per_scenario: int, max_move_no_response_size: int, max_attack_size: int,
                 num_MCTS_sims: int, cpuct: float, max_depth: int = 100
                 ):

        self.puppet = {
            RED: Puppet(RED),
            BLUE: Puppet(BLUE),
        }

        self.seed: int = seed
        self.random = np.random.default_rng(self.seed)
        self.gm: GameManager = GameManager(self.seed)
        self.mm: MatchManager = None

        self.nnet: dict[Tuple(str, str), ModelWrapper] = {
            (RED, ACT): nnet_RED_Act,
            (RED, RES): nnet_RED_Res,
            (BLUE, ACT): nnet_BLUE_Act,
            (BLUE, RES): nnet_BLUE_Res,
        }

        self.Qsa = {}  # stores Q values for (s, a)
        self.Nsa = {}  # stores #times edge (s, a) was visited
        self.Ns = {}  # stores #times board (s) was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # is this the end or not?
        self.Vs = {}  # stores action indices for (s)
        self.VAs = {}  # stores actions themselves for (s)

        self.states: list = []  # stores hash states

        self.num_MCTS_sims: int = num_MCTS_sims
        self.cpuct: float = cpuct
        self.max_depth: int = max_depth

        self.max_weapon_per_figure: int = max_weapon_per_figure
        self.max_figure_per_scenario: int = max_figure_per_scenario
        self.max_move_no_response_size: int = max_move_no_response_size
        self.max_action_size: int = max_move_no_response_size + max_attack_size + 1  # input vector size

    def generateFeatures(self, board: GameBoard, state: GameState) -> np.ndarray:

        board = np.zeros(board.shape)

        for f in state.figures[RED]:
            board[f.position.tuple()] = int(f.index + 1)

        for f in state.figures[BLUE]:
            board[f.position.tuple()] = -int(f.index - 1)

        return board

    def calculateValidMoves(self, gm, board, state, team, action_type):
        all_valid_actions = []

        if action_type == "Action":
            all_valid_actions = gm.buildActionsForTeam(board, state, team)

        elif action_type == "Response":
            all_valid_actions = gm.buildResponsesForTeam(board, state, team)

        return all_valid_actions

    def actionIndexMapping(self, gm, board, state, team, action_type):
        all_valid_actions = self.calculateValidMoves(gm, board, state, team, action_type)

        valid_indices = [0] * self.max_action_size
        valid_actions = [None] * self.max_action_size

        if all_valid_actions != []:

            for a in all_valid_actions:
                idx = -1

                if type(a) == AttackResponse or type(a) == Attack:

                    figure_ind = a.figure_id
                    target_ind = a.target_id

                    weapon_ind = WEAPONS_INDICES[a.weapon_id]

                    idx = (
                        self.max_move_no_response_size +
                        weapon_ind +
                        target_ind * self.max_weapon_per_figure +
                        figure_ind * self.max_weapon_per_figure * self.max_figure_per_scenario
                    )

                elif type(a) == Wait:

                    idx = self.max_move_no_response_size - 2

                elif type(a) == NoResponse:

                    idx = self.max_move_no_response_size - 1

                elif type(a) == PassTeam:

                    idx = self.max_move_no_response_size

                else:

                    if type(a) == PassFigure:
                        x = 0
                        y = 0

                    elif type(a) == Move:

                        start_pos = a.position.tuple()
                        end_pos = a.destination.tuple()

                        x = end_pos[0] - start_pos[0]
                        y = end_pos[1] - start_pos[1]

                    elif type(a) == MoveLoadInto:

                        start_pos = a.position.tuple()
                        end_pos = a.destination.tuple()

                        x = end_pos[0] - start_pos[0]
                        y = end_pos[1] - start_pos[1]

                    figure_index = a.figure_id

                    if x+y <= 0:
                        index_shift = ((x+y+(7+7))*(x+y+(7+7+1)))//2+y+7
                    else:
                        index_shift = 224-(((x+y-(7+7))*(x+y-(7+7+1)))//2-y-7)

                    idx = figure_index * 225 + index_shift

                valid_indices[idx] = 1
                valid_actions[idx] = a

        return valid_indices, valid_actions

    def mapTeamMoveIntoID(self, team, action_type):
        if team == RED and action_type == "Action":
            return 0
        elif team == RED and action_type == "Response":
            return 1
        elif team == BLUE and action_type == "Action":
            return 2
        elif team == BLUE and action_type == "Response":
            return 3

    def getActionProb(self, board, state, team, move_type, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS 

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        start_state = deepcopy(state)
        start_team = team
        start_move_type = move_type

        if not self.mm:
            self.mm = MatchManager('MCTS', self.puppet[RED], self.puppet[BLUE], board, state, self.seed, False)

        old_s = -1

        for i in range(self.num_MCTS_sims):
            logger.debug('MCTS SIMULATION %s', i)
            self.search(board, start_state, old_s, self.max_depth)

        team_move_id = self.mapTeamMoveIntoID(start_team, start_move_type)

        s = 0
        i = 0

        start_state_hash = hash(start_state)
        while i < len(self.states):
            if start_state_hash == self.states[i][0] and team_move_id == self.states[i][1]:
                s = i
                break
            else:
                i += 1

        logger.debug('getActProb S is: %s and his parent: %s', s, old_s)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.max_action_size)]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = self.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs, s

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs, s

    def search(self, board, state, old_s, depth):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        # load current state in internal match manager
        self.mm.loadState(board, state)
        action_type, team, _ = self.mm.nextPlayer()

        if action_type in ('update', 'init', 'end'):
            self.mm.nextStep()
            state = self.mm.state
            action_type, team, _ = self.mm.nextPlayer()

            # this is to avoid 'update -> end' stuck
            if action_type == 'end':
                self.mm.nextStep()
                state = self.mm.state
                action_type, team, _ = self.mm.nextPlayer()

        action_type = ACT if action_type == 'round' else RES

        # generate data vector
        features = self.generateFeatures(board, state)

        i = 0
        s = -1

        # map move and action type to id
        team_move_id = self.mapTeamMoveIntoID(team, action_type)

        state_hash = hash(state)
        while i < len(self.states):
            if state_hash == self.states[i][0] and team_move_id == self.states[i][1]:
                s = i
                break
            else:
                i += 1

        if s == -1:
            self.states.append((state_hash, team_move_id))
            s = len(self.states)-1

        logger.debug('S is: %s and his parent is: %s', s, old_s)

        # check for end of the game
        if s not in self.Es:
            isEnd, winner = self.mm.end, self.mm.winner
            if not isEnd:
                self.Es[s] = 0
            elif winner == team:
                self.Es[s] = 1
            else:
                self.Es[s] = -1

        if self.Es[s] != 0:
            # terminal node
            logger.debug('end, S=%s', s)
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node, no probabilities assigned yet

            valid_s = [0] * self.max_action_size  # [0]*5851 #self.numMaxActions(board, state)
            valid_actions = [None] * self.max_action_size

            self.Ps[s], v = self.nnet[(team, action_type)].predict(features)

            valid_s, valid_actions = self.actionIndexMapping(self.gm, board, state, team, action_type)

            self.Ps[s] = self.Ps[s] * valid_s  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])

            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                logger.error("All valid moves were masked, doing a workaround.")

                self.Ps[s] = self.Ps[s] + valid_s
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valid_s
            self.VAs[s] = valid_actions
            self.Ns[s] = 0
            return -v

        valid_s = self.Vs[s]
        valid_actions = self.VAs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.max_action_size):
            if valid_s[a]:
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                        1 + self.Nsa[(s, a)])
                else:
                    u = self.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act

        old_s = s

        action = valid_actions[a]

        state, _ = self.gm.activate(board, state, action)

        if depth == 0:
            return 0

        v = self.search(board, state, old_s, depth-1)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v
