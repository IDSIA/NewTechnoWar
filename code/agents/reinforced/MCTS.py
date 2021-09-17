# MCTS

import logging
import math
from typing import Dict, Tuple

import numpy as np

from core.game import GameManager, GameBoard, GameState
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam, AttackResponse, PassFigure, Wait, MoveLoadInto
from core.const import RED, BLUE

from agents import MatchManager, Puppet
from agents.reinforced.nn import ModelWrapper
from agents.reinforced.utils import ACT, RES
from utils.copy import deepcopy

logger = logging.getLogger(__name__)

EPS: float = 1e-8

WEAPONS_INDICES: Dict[str, int] = {
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

    def __init__(self, model_red: ModelWrapper, model_blue: ModelWrapper,
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

        self.nnet: Dict[Tuple(str, str), ModelWrapper] = {
            RED: model_red,
            BLUE: model_blue,
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

        terrain = board.terrain.copy()
        goals = np.zeros(board.shape)
        figures = np.zeros(board.shape)

        for mark in board.getObjectiveMark():
            goals[mark.tuple()] = 1

        for f in state.figures[RED]:
            figures[f.position.tuple()] = int(f.index + 1)

        for f in state.figures[BLUE]:
            figures[f.position.tuple()] = -int(f.index - 1)

        return np.stack((figures, goals, terrain))

    def calculateValidMoves(self, board, state, team, action_type) -> np.ndarray:
        all_valid_actions = []

        if action_type == ACT:
            all_valid_actions = self.gm.buildActionsForTeam(board, state, team)

        elif action_type == RES:
            all_valid_actions = self.gm.buildResponsesForTeam(board, state, team)

        return np.array(all_valid_actions)

    def actionIndexMapping(self, board, state, team, action_type) -> Tuple[np.ndarray, np.ndarray]:
        all_valid_actions = self.calculateValidMoves(board, state, team, action_type)

        valid_indices = np.array([False] * self.max_action_size)
        valid_actions = np.array([None] * self.max_action_size)

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

            valid_indices[idx] = True
            valid_actions[idx] = a

        return valid_indices, valid_actions

    def mapTeamMoveIntoID(self, team, action_type) -> int:
        if team == RED and action_type == ACT:
            return 0
        elif team == RED and action_type == RES:
            return 1
        elif team == BLUE and action_type == ACT:
            return 2
        elif team == BLUE and action_type == RES:
            return 3

    def getActionProb(self, board, state, team, move_type, temp=1) -> Tuple[np.ndarray, int]:
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
            state_hash, move_id = self.states[i]
            if start_state_hash == state_hash and team_move_id == move_id:
                s = i
                break
            else:
                i += 1

        logger.debug('getActProb S is: %s and his parent: %s', s, old_s)
        counts = np.nan_to_num(np.array([self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.max_action_size)])).astype(np.float64)

        if temp == 0:
            bestAs = (np.argwhere(counts == np.max(counts))).flatten()
            bestA = self.random.choice(bestAs)
            probs = np.zeros(counts.shape)
            probs[bestA] = 1
            return probs, s

        counts = np.nan_to_num(np.power(counts, (1. / temp)))
        probs = counts / counts.sum()
        return probs, s

    def search(self, board, state, old_s, depth) -> float:
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

        if self.Es[s] != 0 or depth == 0:
            # terminal node
            logger.debug('end, S=%s', s)
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node, no probabilities assigned yet
            valid_s, valid_actions = self.actionIndexMapping(board, state, team, action_type)

            features = self.generateFeatures(board, state)

            self.Ps[s], v = self.nnet[team].predict(features)
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
                    u = self.Qsa[(s, a)] + self.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (1 + self.Nsa[(s, a)])
                else:
                    u = self.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act

        old_s = s

        action = valid_actions[a]

        state, _ = self.gm.activate(board, state, action)

        v = self.search(board, state, old_s, depth - 1)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v
