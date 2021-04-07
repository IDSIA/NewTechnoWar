from typing import Tuple, List

import numpy as np

from agents import AlphaBetaAgent
from core.actions import Action, Move, Attack, Response
from core.const import RED, BLUE
from core.game import GoalParams, GameBoard, GameState, GoalReachPoint


class AlphaBetaFast1Agent(AlphaBetaAgent):

    def __init__(self, team: str, searchDepth: int = 2, maxSearchTime: int = 60, a: float = 1.0, b: float = 1.0,
                 c: float = 0.1, d: float = 0.1):
        super().__init__(team, searchDepth, maxSearchTime)
        self.name = 'AlphaBetaFast1Agent'
        self.forceHit = True

        self.boardValues: GoalReachPoint or None = None

        self.a: float = a
        self.b: float = b
        self.c: float = c
        self.d: float = d

    def evaluateState(self, team: str, params: GoalParams, board: GameBoard, state: GameState) -> float:
        if state.turn >= board.maxTurn:
            return -5

        value: float = 0
        bv: np.ndarray = self.boardValues.values
        courage: float = 1 / (1 - state.turn / board.maxTurn + np.exp(-5))

        a: float = self.a
        b: float = self.b  # * (1-courage)
        c: float = self.c * courage
        d: float = self.d  # * courage

        other: str = RED if self.team == BLUE else BLUE

        # ally figures alive increase value of the state
        for figure in state.figures[self.team]:
            if not figure.killed:
                value += (a + c * bv[figure.position.tuple()])  # the prefactor is fully ad hoc. should be tuned

        # enemy figures alive reduce value of the state
        for figure in state.figures[other]:
            if not figure.killed:
                value -= (b + d * bv[figure.position.tuple()])  # the prefactor is fully ad hoc. should be tuned

        return value

    def nextActions(self, team: str, step: str, board: GameBoard, state: GameState, depth: int) -> List[Action]:
        nextActions = []
        if step == 'response':
            nextActions += [self.gm.actionPassResponse(team)]
            for figure in state.getFiguresCanRespond(team):
                nextActions += self.gm.buildResponses(board, state, figure)
        else:
            for figure in state.getFiguresCanBeActivated(team):
                nextActions += [self.gm.actionPassFigure(figure)]

                if self.maxDepth - depth == 0:
                    nextActions += self.gm.buildMovements(board, state, figure)
                nextActions += self.gm.buildAttacks(board, state, figure)
        return nextActions

    def probabilitySuccessfulAttack(self, board: GameBoard, state: GameState, action: Action) -> float:
        _, outcome = self.activateAction(board, state, action)  # this generates a new state, that we ignore
        return outcome['hitScore'] / 20.0

    def listOfPossibleRespondersToMove(self, team: str, board: GameBoard, state: GameState, action: Action) -> List[
        Response]:
        """
        @param team: other team
        @param board: current board to use
        @param state: current state to use
        @param figureMoved: figure that moved and generated the current state
        @return: a list of figures that can respond to the figure
        """
        responders = []

        for figure in state.getFiguresCanRespond(team):
            responders += self.mm.gm.buildResponses(board, state, figure, action)

        return responders

    def probSuccessfulResponseCumulative(self, team: str, board: GameBoard, state: GameState, action: Action):
        prob: float = 0

        for figure in state.getFiguresCanRespond(team):
            for response in self.mm.gm.buildResponses(board, state, figure, action):
                r = self.probabilitySuccessfulAttack(board, state, response)
                prob = max(prob, r)

        return prob

    def apply(self, board: GameBoard, state: GameState, action: Action, alpha: float, beta: float, depth: int,
              startTime: int, timeLimit: int) -> float:

        self.evaluateState(action.team)
        s1, outcome = self.activateAction(board, state, action)

        if isinstance(action, Move):
            pResponse: float = self.probSuccessfulResponseCumulative('', board, state, action)
            pNoResponse: float = 1 - pResponse

            noResponseScore: float = self.evaluateState()
            responseScore: float = self.evaluateState()

            score = pResponse * responseScore * pNoResponse * noResponseScore

        elif isinstance(action, Attack):

            noEffectScore: float = 0

            pAction: float = 0
            pNoAction: float = 1 - pAction

            actionScore: float = self.evaluateState()
            pResponse: float = self.probSuccessfulResponseCumulative('', board, state, action)
            pNoResponse: float = 1 - pResponse

            noResponseScore: float = self.evaluateState()
            responseScore: float = self.evaluateState()

            score = pAction * actionScore + pNoAction * (pResponse * responseScore + pNoResponse * noEffectScore)

        else:  # this is pass
            score, _ = self.alphaBeta(board, state, depth - 1, alpha, beta, startTime, timeLimit)

        return score

    def search(self, board: GameBoard, state: GameState) -> Tuple[float, Action]:
        if not self.boardValues:
            # this is done only once for the first search since we assume that the board does not change over time
            self.boardValues = GoalReachPoint(self.team, board.shape, board.getObjectiveMark())

        return super().search(board, state)
