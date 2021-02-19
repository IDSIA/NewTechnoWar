import logging
import math
from time import time

from agents import Agent, MatchManager, GreedyAgent
from agents.adversarial.puppets import Puppet
from agents.commons import stateScore
from core import GM
from core.actions import Action
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import GoalParams
from core.game.state import GameState
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class AlphaBetaAgent(Agent):

    def __init__(self, team: str, maxDepth: int = 3, timeLimit: int = 20):
        super().__init__('AlphaBetaAgent', team)

        self.maxDepth: int = maxDepth
        self.cache: dict = {}
        self.goal_params: GoalParams = GoalParams()
        self.timeLimit = timeLimit

        self.puppets: dict = {RED: Puppet(RED), BLUE: Puppet(BLUE)}
        self.mm: MatchManager = MatchManager('', self.puppets[RED], self.puppets[BLUE])

        self.searchCutOff: bool = False

    def activateAction(self, board, state, action):
        hashState0 = hash(state)
        hashAction = hash(action.__str__())

        key = (hashState0, hashAction)

        if key in self.cache:
            return self.cache[key]

        else:
            state1, _ = GM.activate(board, state, action)
            self.cache[key] = state1
            return state1

    def alphaBeta(self, board: GameBoard, state: GameState, depth, alpha, beta, startTime, timeLimit):
        currentTime = time()
        elapsedTime = currentTime - startTime

        if elapsedTime >= timeLimit:
            self.searchCutOff = True

        self.mm.loadState(board, state)
        step, team, _ = self.mm.nextPlayer()

        # if an update is required
        if step == 'update':
            self.mm.step()
            step, team, _ = self.mm.nextPlayer()

        # if this is a terminal node, abort the search
        if self.searchCutOff or depth == 0 or step == 'end' or team == '':
            score = stateScore(self.team, self.goal_params, board, state)
            return score, None

        # build actions
        nextActions = []

        if step == 'response':
            nextActions += [GM.actionPassResponse(team)]
            for figure in state.getFiguresCanRespond(team):
                nextActions += GM.buildResponses(board, state, figure)
        else:
            for figure in state.getFiguresCanBeActivated(team):
                nextActions += [GM.actionPassFigure(figure)]

                # standard actions
                nextActions += GM.buildAttacks(board, state, figure)
                nextActions += GM.buildMovements(board, state, figure)

        # this team maximize...
        if team == self.team:
            value = -math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                # s1, _ = GM.activate(board, state, nextAction)
                s1 = self.activateAction(board, state, nextAction)
                score, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)

                if score > value:
                    value, action = score, nextAction
                    logging.debug(f'       AB{depth}: Max {action} [{score}]')

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value, action

        # ...other minimize
        else:
            value = math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                s1, _ = GM.activate(board, state, nextAction)
                score, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)

                if score < value:
                    value, action = score, nextAction
                    logging.debug(f'       AB{depth}: Min {action} [{score}]')

                beta = min(beta, value)

                if beta <= alpha:
                    break

            return value, action

    def search(self, board, state):
        """Using iterative deepening search."""

        # TODO: find a better log management...
        logger.disabled = True

        startTime = time()
        endTime = startTime + self.timeLimit
        score = 0
        action = None
        self.searchCutOff = False

        for depth in range(1, self.maxDepth):
            currentTime = time()

            if currentTime >= endTime:
                break

            score, action = self.alphaBeta(board, state, depth, -math.inf, math.inf, currentTime, endTime - currentTime)

        logger.disabled = False

        if not action:
            raise ValueError('no action given')

        return score, action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        _, action = self.search(board, state)
        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        _, action = self.search(board, state)
        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """Uses GreedyAgent placer method."""
        # TODO: find a better placer
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        """Plays a game for each color and choose the best score."""
        colors = list(state.choices[self.team].keys())

        max_color = None
        max_value = -math.inf

        for color in colors:
            s: GameState = deepcopy(state)
            s.choose(self.team, color)
            score, _ = self.search(board, s)

            if score > max_value:
                max_value = score
                max_color = color

        state.choose(self.team, max_color)
        logging.info(f'{self.team:5}: choose positions color {max_color}')
