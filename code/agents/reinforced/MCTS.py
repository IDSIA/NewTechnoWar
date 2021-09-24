# MCTS

from core.actions.attacks import AttackFigure, AttackGround
from core.figures.lists import WEAPON_KEY_LIST
import logging
import math
from typing import Dict, Tuple

import numpy as np

from core.game import GameManager, GameBoard, GameState, GoalParams, MAX_UNITS_PER_TEAM
from core.actions import Move, MoveLoadInto, AttackFigure, AttackGround, AttackResponse, NoResponse, PassTeam, PassFigure, Wait
from core.const import RED, BLUE

from agents import MatchManager, Puppet
from agents.reinforced.nn import ModelWrapper
from agents.reinforced.utils import ACT, RES
from utils.copy import deepcopy

logger = logging.getLogger(__name__)

EPS: float = 1e-8


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(
        self, shape: Tuple[int, int], model_red: ModelWrapper, model_blue: ModelWrapper, seed: int = -1, num_MCTS_sims: int = 30, cpuct: float = 1.0, max_depth: int = 100, max_units_per_team: int = MAX_UNITS_PER_TEAM
    ):
        """
        shape:                  Board size
        model_red:              ModelWrapper to use for red (must be compatible with 'shape' and 'max_figures_per_team')
        model_blue:             ModelWrapper to use for red (must be compatible with 'shape' and 'max_figures_per_team')
        seed:                   Random seed
        num_MCTS_sims:          Number of total simulation
        cpuct:                  Heuristic search parameter
        max_depth:              Max depth of the search tree
        max_units_per_team:     Number of units in each team (default: MAX_UNITS_PER_TEAM)
        """
        x, y = shape

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

        self.max_units_per_team: int = max_units_per_team
        self.n_weapons: int = len(WEAPON_KEY_LIST)

        self.action_size = (
            # moves
            self.max_units_per_team * x * y
            # attacks
            + self.max_units_per_team * self.n_weapons * x * y
            # response
            + self.max_units_per_team * self.n_weapons * x * y
            # pass-figure
            + self.max_units_per_team
            # pass-team, wait, no-response
            + 3
        )

    def generateFeatures(self, board: GameBoard, state: GameState, is_response: bool) -> np.ndarray:
        # TODO: consider the features from a team point of view

        # build board features
        terrain = board.terrain.copy()
        protection = board.protectionLevel.copy()

        board_fig = {
            RED: np.zeros(board.shape),
            BLUE: np.zeros(board.shape),
        }

        for team in [RED, BLUE]:
            for f in state.figures[team]:
                board_fig[team][f.position.tuple()] = f.index + 1

        goals = {
            RED: np.zeros(board.shape),
            BLUE: np.zeros(board.shape),
        }

        for team in [RED, BLUE]:
            other = RED if team is BLUE else BLUE
            team_goals = board.objectives[team]

            if 'GoalReachPoint' in team_goals or 'GoalDefendPoint' in team_goals:
                for mark in board.getObjectiveMark():
                    goals[team][mark.tuple()] = 10

            if 'GoalEliminateOpponent' in team_goals:
                goals[team] += board_fig[team]
                goals[team] -= board_fig[other]

        feat_board = np.stack([board_fig[RED], board_fig[BLUE], goals[RED], goals[BLUE], protection, terrain])

        # TODO: personalize paraemters
        # params = GoalParams()

        meta = np.array([board.maxTurn, is_response, ], np.float64)

        # build state features
        feat_state = np.concatenate([meta, state.vector()], axis=0)

        return feat_board.astype(np.float64), feat_state.astype(np.float64)

    def calculateValidMoves(self, board, state, team, action_type) -> np.ndarray:
        all_valid_actions = []

        if action_type == ACT:
            all_valid_actions = self.gm.buildActionsForTeam(board, state, team)

        elif action_type == RES:
            all_valid_actions = self.gm.buildResponsesForTeam(board, state, team)

        return np.array(all_valid_actions)

    def actionIndexMapping(self, board, state, team, action_type) -> Tuple[np.ndarray, np.ndarray]:
        all_valid_actions = self.calculateValidMoves(board, state, team, action_type)

        board_x, board_y = board.shape

        move_idx = np.zeros((self.max_units_per_team, board_x, board_y), bool)
        move_act = np.empty((self.max_units_per_team, board_x, board_y), object)
        attack_idx = np.zeros((self.max_units_per_team, self.n_weapons, board_x, board_y), bool)
        attack_act = np.empty((self.max_units_per_team, self.n_weapons, board_x, board_y), object)
        resp_idx = np.zeros((self.max_units_per_team, self.n_weapons, board_x, board_y), bool)
        resp_act = np.empty((self.max_units_per_team, self.n_weapons, board_x, board_y), object)
        pass_idx = np.zeros((self.max_units_per_team), bool)
        pass_act = np.empty((self.max_units_per_team), object)
        extra_idx = np.zeros((3), bool)
        extra_act = np.empty((3), object)

        for a in all_valid_actions:

            if type(a) == Move or type(a) == MoveLoadInto:
                figure_id = a.figure_id

                x, y = a.destination.tuple()

                move_idx[figure_id, x, y] = 1.0
                move_act[figure_id, x, y] = a

            elif type(a) == AttackGround:
                figure_id = a.figure_id

                x, y = a.ground.tuple()
                w = a.weapon_idx

                resp_idx[figure_id, w, x, y] = 1.0
                resp_act[figure_id, w, x, y] = a

            elif type(a) == AttackResponse:
                figure_id = a.figure_id

                x, y = a.target_pos.tuple()
                w = a.weapon_idx

                resp_idx[figure_id, w, x, y] = 1.0
                resp_act[figure_id, w, x, y] = a

            elif type(a) == AttackFigure:
                figure_id = a.figure_id

                x, y = a.target_pos.tuple()
                w = a.weapon_idx

                attack_idx[figure_id, w, x, y] = 1.0
                attack_act[figure_id, w, x, y] = a

            elif type(a) == PassTeam:
                extra_idx[0] = 1.0
                extra_act[0] = a

            elif type(a) == Wait:
                extra_idx[1] = 1.0
                extra_act[1] = a

            elif type(a) == NoResponse:
                extra_idx[2] = 1.0
                extra_act[2] = a

            elif type(a) == PassFigure:
                figure_id = a.figure_id

                pass_idx[figure_id] = 1.0
                pass_act[figure_id] = a

        valid_indices = np.concatenate([
            move_idx.reshape(-1),
            attack_idx.reshape(-1),
            resp_idx.reshape(-1),
            pass_idx.reshape(-1),
            extra_idx.reshape(-1)]
        )
        valid_actions = np.concatenate([
            move_act.reshape(-1),
            attack_act.reshape(-1),
            resp_act.reshape(-1),
            pass_act.reshape(-1),
            extra_act.reshape(-1)]
        )

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
        This function performs num_MCTS_sims simulations of MCTS.

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
        counts = np.array([self.Nsa.get((s, a), 0) for a in range(self.action_size)])

        if counts.sum() == 0:
            logger.debug('empty counts array in mcts')
            counts = np.ones(counts.shape)

        if temp == 0:
            bestAs = np.argwhere(counts == np.max(counts)).flatten()
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

            x_b, x_s = self.generateFeatures(board, state, action_type == RES)

            self.Ps[s], v = self.nnet[team].predict([x_b], [x_s])
            self.Ps[s] = self.Ps[s] * valid_s  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])

            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                # logger.error("All valid moves were masked, doing a workaround.")

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
        for a in range(self.action_size):
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
