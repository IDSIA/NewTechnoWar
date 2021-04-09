import logging
import math
from time import time
from typing import Tuple, List

from agents import Agent, MatchManager, GreedyAgent
from agents.adversarial.puppets import Puppet
from agents.commons import stateScore
from core.actions import Action
from core.const import RED, BLUE
from core.game import GameBoard, GameState, GoalParams
from core.game.outcome import Outcome
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class AlphaBetaAgent(Agent):

    def __init__(self, team: str, maxDepth: int = 3, timeLimit: int = 20, seed: int = 42):
        super().__init__('AlphaBetaAgent', team)

        self.maxDepth: int = maxDepth
        self.cache: dict = {}
        self.goal_params: GoalParams = GoalParams()
        self.timeLimit: int = timeLimit

        self.puppets: dict = {RED: Puppet(RED), BLUE: Puppet(BLUE)}
        self.mm: MatchManager = MatchManager('', self.puppets[RED], self.puppets[BLUE], seed=seed, useLoggers=False)

        self.searchCutOff: bool = False
        self.forceHit: bool = False

    def activateAction(self, board: GameBoard, state: GameState, action: Action) -> Tuple[GameState, Outcome]:
        hashState0 = hash(state)
        hashAction = hash(action.__str__())

        key = (hashState0, hashAction)

        if key in self.cache:
            return self.cache[key]

        else:
            state1, outcome = self.gm.activate(board, state, action, self.forceHit)
            self.cache[key] = state1, outcome
            return state1, outcome

    def evaluateState(self, team: str, board: GameBoard, state: GameState, params: GoalParams) -> float:
        return stateScore(team, params, board, state)

    def nextActions(self, team: str, board: GameBoard, state: GameState, step: str, depth: int) -> List[Action]:
        nextActions = []
        if step == 'response':
            nextActions += [self.gm.actionPassResponse(team)]
            for figure in state.getFiguresCanRespond(team):
                nextActions += self.gm.buildResponses(board, state, figure)
        else:
            for figure in state.getFiguresCanBeActivated(team):
                nextActions += [self.gm.actionPassFigure(figure)]

                # standard actions
                nextActions += self.gm.buildAttacks(board, state, figure)
                nextActions += self.gm.buildMovements(board, state, figure)
        return nextActions

    def apply(self, board: GameBoard, state: GameState, action: Action, step: str, alpha: float, beta: float,
              depth: int, startTime: float, timeLimit: float) -> float:
        s1, _ = self.activateAction(board, state, action)
        score, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)
        return score

    def alphaBeta(self, board: GameBoard, state: GameState, depth: int, alpha: float, beta: float, startTime: float,
                  timeLimit: float) -> Tuple[float, Action or None]:
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
            score = self.evaluateState(self.team, board, state, self.goal_params)
            return score, None

        # build actions
        nextActions = self.nextActions(team, board, state, step, depth)

        # this team maximize...
        if team == self.team:
            value = -math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                score = self.apply(board, state, nextAction, step, alpha, beta, depth, startTime, timeLimit)

                if score > value:
                    value, action = score, nextAction
                    logging.debug(f'      AB{depth}: Max {action} [{score}]')

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

                score = self.apply(board, state, nextAction, step, alpha, beta, depth, startTime, timeLimit)

                if score < value:
                    value, action = score, nextAction
                    logging.debug(f'       AB{depth}: Min {action} [{score}]')

                beta = min(beta, value)

                if beta <= alpha:
                    break

            return value, action

    def search(self, board: GameBoard, state: GameState) -> Tuple[float, Action]:
        """Using iterative deepening search."""

        # TODO: find a better log management...
        logger.disabled = True

        startTime: float = time()
        endTime: float = startTime + self.timeLimit
        score: float = 0
        action: Action or None = None
        self.searchCutOff = False

        for depth in range(1, self.maxDepth):
            currentTime: float = time()

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
