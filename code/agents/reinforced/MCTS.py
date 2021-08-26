# MCTS

import logging
import math

import numpy as np
from agents.adversarial.puppets import Puppet

from core.game import GameManager, goalAchieved
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam, AttackResponse, PassFigure, AttackGround, MoveLoadInto
from core.const import RED, BLUE
from core.vectors import vectorBoard
from core.figures import Figure

from agents import MatchManager
from agents.reinforced.utils import actionIndexMapping, calculateValidMoves, mapTeamMoveIntoID, WEAPONS_INDICES

EPS = 1e-8

logger = logging.getLogger(__name__)


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, board, state, team, moveType, nnet_RED_Act, nnet_RED_Res, nnet_BLUE_Act, nnet_BLUE_Res, args):
        self.board = board
        self.state = state
        self.team = team
        self.moveType = moveType

        puppy_red = Puppet(RED)
        puppy_blue = Puppet(BLUE)

        self.seed = args.seed
        self.random = np.random.default_rng(self.seed)
        self.gm = GameManager(self.seed)
        self.mm = MatchManager('', puppy_red, puppy_blue, board, state, useLoggers=False, seed=args.seed)

        self.nnet_RED_Act = nnet_RED_Act
        self.nnet_RED_Res = nnet_RED_Res
        self.nnet_BLUE_Act = nnet_BLUE_Act
        self.nnet_BLUE_Res = nnet_BLUE_Res

        self.args = args
        self.Qsa = {}  # stores Q values for (s, a)
        self.Nsa = {}  # stores #times edge (s, a) was visited
        self.Ns = {}  # stores #times board (s) was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # is this the end or not?
        self.Vs = {}  # stores action indices for (s)
        self.VAs = {}  # stores actions themselves for (s)
        self.states = []  # stores states

        self.maxWeaponPerFigure = args.maxWeaponPerFigure
        self.maxFigurePerScenario = args.maxFigurePerScenario
        self.maxMoveNoResponseSize = args.maxMoveNoResponseSize
        self.maxActionSize = args.maxMoveNoResponseSize + args.maxAttackSize  # input vector size

    def numMaxActions(self, board, state):
        return self.maxActionSize  # 5851 # TODO: define for each scenario separately

    def generateBoard(self, state):

        board = np.zeros(self.board.shape)  # (16,16)  # TODO: change size

        cube_coords = list(state.posToFigure['red'].keys())
        for i in range(len(cube_coords)):
            board[cube_coords[i].tuple()] = int(state.figures['red'][i].index+1)

        cube_coords = list(state.posToFigure['blue'].keys())
        for i in range(len(cube_coords)):
            board[cube_coords[i].tuple()] = -int(state.figures['blue'][i].index+1)

        return board  # .tostring()

    def getActionProb(self, board, state, team, move_type, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS 

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        start_state = state
        start_team = team  # self.team
        start_move_type = move_type  # "Action" #self.moveType
        last_action = None
        old_s = -1

        for i in range(self.args.numMCTSSims):
            print('MCTS SIMULATION', i)
            self.search(board, start_state, old_s)

        team_move_id = mapTeamMoveIntoID(start_team, start_move_type)

        s = 0
        i = 0

        while i < len(self.states):
            if start_state.__eq__(self.states[i][0]) and team_move_id == self.states[i][1]:
                s = i
                break
            else:
                i += 1
        print('getActProb S is: ', s, 'and his parent:', old_s)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.maxActionSize)]  # range(5851)]

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

    def search(self, board, state, old_s):
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
            self.mm.nextStep()  # this will update the values in the 'state' variable!
            state = self.mm.state
            action_type, team, _ = self.mm.nextPlayer()

            # this is to avoid 'update -> end' stuck
            if action_type == 'end':
                self.mm.nextStep()  # this will update the values in the 'state' variable!
                state = self.mm.state
                action_type, team, _ = self.mm.nextPlayer()

        action_type = 'Action' if action_type == 'round' else 'Response'
        other_team = BLUE if team == RED else RED

        # generate data vector
        wholeStatDynBoard = self.generateBoard(state)

        i = 0
        s = -1

        # map move and action type to id
        team_move_id = mapTeamMoveIntoID(team, action_type)

        while i < len(self.states):
            if state == self.states[i][0] and team_move_id == self.states[i][1]:
                s = i
                break
            else:
                i += 1

        if s == -1:
            self.states.append((state, team_move_id))
            s = len(self.states)-1

        print('S is: ', s, 'and his parent is:', old_s)

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
            print('end, S= ', s)
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node, no probabilities assigned yet

            valid_s = [0] * self.maxActionSize  # [0]*5851 #self.numMaxActions(board, state)
            valid_actions = [None] * self.maxActionSize

            if team == RED and action_type == "Action":
                self.Ps[s], v = self.nnet_RED_Act.predict(wholeStatDynBoard)
            elif team == RED and action_type == "Response":
                self.Ps[s], v = self.nnet_RED_Res.predict(wholeStatDynBoard)
            elif team == BLUE and action_type == "Action":
                self.Ps[s], v = self.nnet_BLUE_Act.predict(wholeStatDynBoard)
            elif team == BLUE and action_type == "Response":
                self.Ps[s], v = self.nnet_BLUE_Res.predict(wholeStatDynBoard)

            all_valid_actions = calculateValidMoves(self.gm, board, state, team, action_type)

            # if all_valid_actions == []:
            #     # does the opponent have valid moves?

            #     figToBeActivatedForOtherTeam = self.state.getFiguresCanBeActivated(other_team)
            #     allValidActionsOtherTeam = calculateValidMoves(self.gm, board, state, other_team, "Action")

            #     if allValidActionsOtherTeam:
            #         valid_s[self.maxMoveNoResponseSize] = 1
            #         valid_actions[self.maxMoveNoResponseSize] = PassTeam(team)

            # else:
            valid_s, valid_actions = actionIndexMapping(all_valid_actions, self.maxActionSize, self.maxMoveNoResponseSize, self.maxWeaponPerFigure, self.maxFigurePerScenario)

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
        for a in range(self.maxActionSize):  # range(5851):
            if valid_s[a]:
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                        1 + self.Nsa[(s, a)])
                else:
                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act

        old_s = s

        action = valid_actions[a]

        state, _ = self.gm.activate(board, state, action)

        v = self.search(board, state, old_s)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v
