import logging
from typing import Tuple, List

import numpy as np

from agents import AlphaBetaAgent
from core.actions import Action
from core.const import RED, BLUE
from core.game import GoalParams, GameBoard, GameState, GoalReachPoint

logger = logging.getLogger(__name__)


class AlphaBetaFast1Agent(AlphaBetaAgent):

    def __init__(self, team: str, maxDepth: int = 2, timeLimit: int = 60, baseAllyAlive: float = 1.0,
                 baseEnemyAlive: float = 1.0, coeffAllyAlive: float = 0.1, coeffEnemyAlive: float = 0.1,
                 seed: int = 42):
        super().__init__(team, maxDepth, timeLimit, seed)
        self.name = 'AlphaBetaFast1Agent'
        self.forceHit = True

        self.boardValues: GoalReachPoint or None = None

        self.baseAllyAlive: float = baseAllyAlive
        self.baseEnemyAlive: float = baseEnemyAlive
        self.coeffAllyAlive: float = coeffAllyAlive
        self.coeffEnemyAlive: float = coeffEnemyAlive

    def evaluateState(self, team: str, board: GameBoard, state: GameState, params: GoalParams) -> float:
        if state.turn >= board.maxTurn:
            return -5.0

        bv: np.ndarray = self.boardValues.values
        courage: float = 1.0 / (1.0 - state.turn / board.maxTurn + np.exp(-5.0))

        other: str = RED if self.team == BLUE else BLUE

        value: float = 0.0
        # ally figures alive increase value of the state
        for figure in state.figures[self.team]:
            if not figure.killed:
                value += self.baseAllyAlive + self.coeffAllyAlive * bv[figure.position.tuple()] * courage

        # enemy figures alive reduce value of the state
        for figure in state.figures[other]:
            if not figure.killed:
                value -= self.baseEnemyAlive + self.coeffEnemyAlive * bv[figure.position.tuple()]

        return value

    def nextActions(self, team: str, board: GameBoard, state: GameState, step: str, depth: int) -> List[Action]:
        nextActions = []
        if step == 'response':
            nextActions += [self.gm.actionPassResponse(team)]
            for figure in state.getFiguresCanRespond(team):
                nextActions += self.gm.buildResponses(board, state, figure)

        else:
            for figure in state.getFiguresCanBeActivated(team):
                # RED team can't pass
                if team == BLUE:
                    nextActions += [self.gm.actionPassFigure(figure)]

                if self.maxDepth - depth == 0:
                    nextActions += self.gm.buildMovements(board, state, figure)
                nextActions += self.gm.buildAttacks(board, state, figure)

            # if we don't have actions available we are forced to pass with the whole team
            if not nextActions:
                nextActions += [self.gm.actionPassTeam(team)]

        return nextActions

    def apply(self, board: GameBoard, state: GameState, action: Action, step: str, alpha: float, beta: float,
              depth: int, startTime: int, timeLimit: int) -> float:

        if step == 'response':
            noEffect = self.mm.gm.actionPassResponse(action.team)
        else:
            noEffect = self.mm.gm.actionPassTeam(action.team)

        s0, _ = self.activateAction(board, state, noEffect)
        score0 = self.evaluateState(action.team, board, s0, self.goal_params)

        s1, outcome1 = self.activateAction(board, state, action)  # remember that this is always successful!
        p1 = 1 - outcome1.hitScore / 20.0
        score1, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)

        score: float = (1 - p1) * score0 + p1 * score1

        logger.debug(f'depth={depth} step={step} score={score}')

        return score

    def search(self, board: GameBoard, state: GameState) -> Tuple[float, Action]:
        if not self.boardValues:
            # this is done only once for the first search since we assume that the board does not change over time
            self.boardValues = GoalReachPoint(self.team, board.shape, board.getObjectiveMark())

        return super().search(board, state)
