import logging
from typing import Tuple, List

import numpy as np

from agents import AlphaBetaAgent
from core.actions import Action
from core.const import RED, BLUE
from core.game import GoalParams, GameBoard, GameState, GoalReachPoint

logger = logging.getLogger(__name__)


class AlphaBetaFast1Agent(AlphaBetaAgent):

    def __init__(self, team: str, maxDepth: int = 2, timeLimit: int = 60, goal_params: GoalParams = GoalParams(),
                 baseAllyAlive: float = 1.0, baseEnemyAlive: float = 1.0, coeffAllyAlive: float = 0.1,
                 coeffEnemyAlive: float = 0.1, seed: int = 42):
        """
        :param team:                the color of the team for this agent
        :param maxDepth:            max search depth (default: 3)
        :param timeLimit:           max execution time in seconds (default: 20)
        :param goal_params:         parameters used for the evaluation of the state
        :param baseAllyAlive:       base score assigned to an alive ally figure (default: 1.0)
        :param baseEnemyAlive:      base score assigned to an alive enemy figure (default: 1.0)
        :param coeffAllyAlive:      coefficient score assigned to an alive ally figure (default: 0.1)
        :param coeffEnemyAlive:     coefficient score assigned to an alive enemy figure (default: 0.1)
        :param seed: internal random seed (default: 42)
        """
        super().__init__(team, maxDepth, timeLimit, goal_params, seed)
        self.name = 'AlphaBetaFast1Agent'
        self.forceHit = True

        self.boardValues: GoalReachPoint or None = None

        self.baseAllyAlive: float = baseAllyAlive
        self.baseEnemyAlive: float = baseEnemyAlive
        self.coeffAllyAlive: float = coeffAllyAlive
        self.coeffEnemyAlive: float = coeffEnemyAlive

    def evaluateState(self, team: str, board: GameBoard, state: GameState) -> float:
        """
        Uses a set of rules based on the expert knowledge to associate a value to the given state. This is similar but
        not equal to what the stateScore() function does.

        :param team:    team to evaluate for
        :param board:   board of the game
        :param state:   the given state to be evaluated
        :return: the score assigned to this state
        """
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
        """
        Builds the possible actions considering that the movements are possible only at the beginning of the
        exploration: this means that all the actions after the first one are Attacks.

        :param team:    find the next actions for this team
        :param board:   board of the game
        :param state:   current state of the game
        :param step:    if "response", this method will generate the possible next actions
        :param depth:   current depth of the exploration
        :return: a list of the available actions that can be applied
        """
        nextActions = []
        if step == 'response':
            nextActions = self.gm.buildResponsesForTeam(board, state, team)

        else:
            nextActions += self.gm.buildWaits(board, state, team)

            for figure in state.getFiguresCanBeActivated(team):
                # RED team can't pass
                if team == BLUE:
                    nextActions += [self.gm.actionPassFigure(figure)]

                if self.maxDepth - depth == 1:
                    nextActions += self.gm.buildMovements(board, state, figure)
                nextActions += self.gm.buildAttacks(board, state, figure)
                nextActions += self.gm.buildSupportAttacks(board, state, figure)

            # if we don't have actions available we are forced to pass with the whole team
            if not nextActions:
                nextActions += [self.gm.actionPassTeam(team)]

        return nextActions

    def apply(self, board: GameBoard, state: GameState, action: Action, step: str, alpha: float, beta: float,
              depth: int, startTime: int, timeLimit: int) -> float:
        """
        Balance the assigned score with the probability of this event to happen.

        :param board:       board of the game
        :param state:       current state
        :param action:      action to apply to the current state
        :param step:        kind of step to perform
        :param alpha:       maximization value
        :param beta:        minimization value
        :param depth:       current depth
        :param startTime:   when the search started
        :param timeLimit:   when the search ended
        :return: the score associated with this exploration
        """

        if step == 'response':
            noEffect = self.mm.gm.actionNoResponse(action.team)
        else:
            noEffect = self.mm.gm.actionPassTeam(action.team)

        s0, _ = self.activateAction(board, state, noEffect)
        score0 = self.evaluateState(action.team, board, s0)

        s1, outcome1 = self.activateAction(board, state, action)  # remember that this is always successful!
        p1 = outcome1.hitScore / 20.0
        score1, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)

        score: float = (1 - p1) * score0 + p1 * score1

        logger.debug(f'depth={depth} step={step} score={score}')

        return score

    def search(self, board: GameBoard, state: GameState) -> Tuple[float, Action]:
        """
        Initialize some internal values after that it continues with the basic search() method.

        :param board:   board of the game
        :param state:   starting state
        :return: a tuple composed by the score and the best Action found
        """
        if not self.boardValues:
            # this is done only once for the first search since we assume that the board does not change over time
            self.boardValues = GoalReachPoint(self.team, board.shape, board.getObjectiveMark())

        return super().search(board, state)
