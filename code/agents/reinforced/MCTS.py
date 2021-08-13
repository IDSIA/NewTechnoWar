# MCTS

import logging
import math

import numpy as np
import core

from core.game import GameManager, goalAchieved
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam
from core.const import RED, BLUE
from core.vectors import vectorBoard
from core.figures import Figure

from agents.reinforced.utils import calculateValidMoves, WEAPONS_INDICES

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

        self.gm = GameManager()

        self.nnet_RED_Act = nnet_RED_Act
        self.nnet_RED_Res = nnet_RED_Res
        self.nnet_BLUE_Act = nnet_BLUE_Act
        self.nnet_BLUE_Res = nnet_BLUE_Res

        self.args = args
        self.Qsa = {}  # stores Q values for s, a
        self.Nsa = {}  # stores #times edge s, a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # is this the end or not?
        self.Vs = {}  # stores action indices for s
        self.VAs = {}  # stores actions themselves for s
        self.states = []  # stores states

        self.maxWeaponPerFigure = args.maxWeaponPerFigure
        self.maxFigurePerScenario = args.maxFigurePerScenario
        self.maxMoveNoResponseSize = args.maxMoveNoResponseSize
        self.maxActionSize = args.maxMoveNoResponseSize + args.maxAttackSize

    def numMaxActions(self, board, state):
        return self.maxActionSize  # 5851 # TODO: define for each scenario separately

    # @staticmethod
    def actionIndexMapping(self, allValidActions):  # TODO: consider Wait actions if needed

        validActionIndicesWrtAllActions = [0] * self.maxActionSize
        validActionWrtAllActions = [None] * self.maxActionSize

        if allValidActions != []:

            for a in allValidActions:
                idx = -1

                if type(a) == core.actions.responses.AttackResponse or type(a) == core.actions.attacks.Attack:

                    figure_ind = a.figure_id
                    target_ind = a.target_id

                    weapon_ind = WEAPONS_INDICES[a.weapon_id]

                    idx = (
                        self.maxMoveNoResponseSize +
                        weapon_ind +
                        target_ind * self.maxWeaponPerFigure +
                        figure_ind * self.maxWeaponPerFigure * self.maxFigurePerScenario
                    )
                elif type(a) == core.actions.responses.NoResponse:

                    idx = self.maxMoveNoResponseSize - 1

                else:

                    if type(a) == core.actions.passes.PassFigure:
                        x = 0
                        y = 0

                    # elif type(a) == core.actions.attacks.Attack: # TODO: add weapons

                    #     start_pos = a.position.tuple()
                    #     end_pos = a.destination.tuple()

                    #     x = end_pos[0] - start_pos[0]
                    #     y = end_pos[1] - start_pos[1]

                    # elif type(a) == core.actions.movements.AttackGround: # TODO: add weapons

                    #     start_pos = a.position.tuple()
                    #     end_pos = a.destination.tuple()

                    #     x = end_pos[0] - start_pos[0]
                    #     y = end_pos[1] - start_pos[1]

                    elif type(a) == core.actions.movements.Move:

                        start_pos = a.position.tuple()
                        end_pos = a.destination.tuple()

                        x = end_pos[0] - start_pos[0]
                        y = end_pos[1] - start_pos[1]

                    elif type(a) == core.actions.movements.MoveLoadInto:

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

                validActionIndicesWrtAllActions[idx] = 1
                validActionWrtAllActions[idx] = a

        return validActionIndicesWrtAllActions, validActionWrtAllActions

    def generateBoard(self, state):

        board = np.zeros(self.board.shape)  # (16,16)  # TODO: change size

        cube_coords = list(state.posToFigure['red'].keys())
        for i in range(len(cube_coords)):
            board[cube_coords[i].tuple()] = int(state.figures['red'][i].index+1)

        cube_coords = list(state.posToFigure['blue'].keys())
        for i in range(len(cube_coords)):
            board[cube_coords[i].tuple()] = -int(state.figures['blue'][i].index+1)

        return board  # .tostring()

    def mapTeamMoveIntoID(self, team, moveType):
        if team == RED and moveType == "Action":
            return 0
        elif team == RED and moveType == "Response":
            return 1
        elif team == BLUE and moveType == "Action":
            return 2
        elif team == BLUE and moveType == "Response":
            return 3

    def getActionProb(self, board, state, team, moveType, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS 

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        start_state = state
        start_team = team  # self.team
        start_moveType = moveType  # "Action" #self.moveType
        lastAction = None
        old_s = -1

        for i in range(self.args.numMCTSSims):
            print('MCTS SIMULATION', i)
            self.search(self.board, start_state, start_team, start_moveType, lastAction, old_s)

        teamMoveID = self.mapTeamMoveIntoID(start_team, start_moveType)

        s = 0
        i = 0

        while i < len(self.states):
            if start_state.__eq__(self.states[i][0]) and teamMoveID == self.states[i][1]:
                s = i
                break
            else:
                i += 1
        print('getActProb S is: ', s, 'and his parent:', old_s)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.maxActionSize)]  # range(5851)]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs, s

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs, s

    def search(self, board, state, team, moveType, lastAction, old_s):
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

        wholeStatDynBoard = self.generateBoard(state)

        i = 0
        s = -1

        teamMoveID = self.mapTeamMoveIntoID(team, moveType)

        while i < len(self.states):
            if state.__eq__(self.states[i][0]) and teamMoveID == self.states[i][1]:
                s = i
                break
            else:
                i += 1
        if s == -1:
            self.states.append((state, teamMoveID))
            s = len(self.states)-1
        print('S is: ', s, 'and his parent is:', old_s)

        if s not in self.Es:
            isEnd, winner = goalAchieved(board, state)
            if not isEnd:
                self.Es[s] = 0
            elif winner == team:
                self.Es[s] = 1
            else:
                self.Es[s] = -1
        if self.Es[s] != 0:
            # terminal node
            print('kraj, S= ', s)
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node
            # no probabilities assigned yet

            valids = [0]*self.maxActionSize  # [0]*5851 #self.numMaxActions(board, state)
            validActions = [None]*self.maxActionSize

            if team == RED and moveType == "Action":
                self.Ps[s], v = self.nnet_RED_Act.predict(wholeStatDynBoard)
            elif team == RED and moveType == "Response":
                self.Ps[s], v = self.nnet_RED_Res.predict(wholeStatDynBoard)
            elif team == BLUE and moveType == "Action":
                self.Ps[s], v = self.nnet_BLUE_Act.predict(wholeStatDynBoard)
            elif team == BLUE and moveType == "Response":
                self.Ps[s], v = self.nnet_BLUE_Res.predict(wholeStatDynBoard)

            allValidActions = calculateValidMoves(board, state, team, moveType)

            if allValidActions == []:
                # does the opponent have valid moves?
                if team == RED:
                    otherTeam = BLUE
                else:
                    otherTeam = RED

                figToBeActivatedForOtherTeam = self.state.getFiguresCanBeActivated(otherTeam)
                allValidActionsOtherTeam = calculateValidMoves(board, state, otherTeam, "Action")

                if allValidActionsOtherTeam:
                    valids[self.maxMoveNoResponseSize] = 1
                    validActions[self.maxMoveNoResponseSize] = PassTeam(team)

            else:

                valids, validActions = self.actionIndexMapping(allValidActions)

            self.Ps[s] = self.Ps[s] * valids  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                logger.error("All valid moves were masked, doing a workaround.")

                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.VAs[s] = validActions
            self.Ns[s] = 0
            return -v

        valids = self.Vs[s]
        validActions = self.VAs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.maxActionSize):  # range(5851):
            if valids[a]:
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                        1 + self.Nsa[(s, a)])
                else:
                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act

        if team == RED and moveType == "Action" and a != self.maxMoveNoResponseSize:
            next_team = BLUE
            next_moveType = "Response"
        elif team == RED and moveType == "Action" and a == self.maxMoveNoResponseSize:
            next_team = BLUE
            next_moveType = "Action"
        elif team == RED and moveType == "Response":
            next_team = RED
            next_moveType = "Action"
        elif team == BLUE and moveType == "Action" and a != self.maxMoveNoResponseSize:
            next_team = RED
            next_moveType = "Response"
        elif team == BLUE and moveType == "Action" and a == self.maxMoveNoResponseSize:
            next_team = RED
            next_moveType = "Action"
        elif team == BLUE and moveType == "Response":
            next_team = BLUE
            next_moveType = "Action"

        old_s = s
        if a == -1:
            self.gm.update(state)
            v = self.search(board, state, RED, "Action", None, old_s)

        else:
            next_s, _ = self.gm.activate(board, state, validActions[a])
            lastAction = validActions[a]
            v = self.search(board, next_s, next_team, next_moveType, lastAction, old_s)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        return -v
