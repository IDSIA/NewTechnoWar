import math
import time

from agents import GreedyAgent
from agents.adversarial import ACTION_PASS, ACTION_MOVE, ACTION_ATTACK
from agents.adversarial.probabilities import probabilityOfSuccessfulResponseAccumulated, probabilityOfSuccessfulAttack
from agents.adversarial.scores import evaluateState, evaluateBoard
from core import RED, BLUE
from core.actions import Action
from core.game.board import GameBoard
from core.game.goals import goalAchieved
from core.game.manager import GameManager
from core.game.state import GameState


class AlphaBetaAgent(GreedyAgent):

    def __init__(self, team: str, maxSearchTime: int = 60, maxDepth: int = 1):
        super().__init__(team)

        self.maxSearchtime: int = maxSearchTime
        self.maxDepth: int = maxDepth
        self.cache: dict = {}

    def _min(self, gm: GameManager, board: GameBoard, state: GameState, alpha, beta, depth, maxRoundDepth, team):
        pass

    def _max(self, gm: GameManager, board: GameBoard, state: GameState, alpha, beta, depth, maxRoundDepth, team):
        # check if hashed
        stateHash = hash(state)
        if stateHash in self.cache:
            return self.cache[stateHash]

        max_value = -math.inf
        action = None
        winner = None

        # check if done
        done, winner = goalAchieved(board, state)
        if done or depth == self.maxDepth:
            return evaluateState(self.boardValues, state), action, winner

        if self.boardValues is None:
            self.boardValues = evaluateBoard(board, self.team)

        other = RED if team == BLUE else BLUE

        # compute all scores for possible actions for each available unit
        for figure in state.getFiguresCanBeActivated(self.team):
            for kind in [ACTION_ATTACK, ACTION_MOVE, ACTION_PASS]:
                actions = []
                if kind == ACTION_ATTACK:
                    actions += gm.buildAttacks(board, state, figure)
                if kind == ACTION_MOVE:
                    actions += gm.buildMovements(board, state, figure)
                if kind == ACTION_PASS:
                    actions += [gm.actionPass(figure)]

                for action in actions:
                    if kind == ACTION_PASS:
                        action = gm.actionPass(figure)
                        s, _ = gm.activate(board, state, action)
                        score = evaluateState(self.boardValues, s), action

                    if kind == ACTION_MOVE:
                        # accumulated probability of a successful response
                        probResponseEffect = probabilityOfSuccessfulResponseAccumulated(gm, board, state, action)

                        # effect of action without enemy response
                        s1, _ = gm.activate(board, state, action)
                        noResponseScore = self._min(gm, board, s1, alpha, beta, depth + 1, maxRoundDepth, other)

                        # effect of action with enemy response killing the unit
                        s2, _ = gm.activate(board, state, action)
                        s2.getFigure(action).killed = True
                        responseScore = evaluateState(self.boardValues, s2)

                        score = (1 - probResponseEffect) * noResponseScore + probResponseEffect * responseScore

                    if kind == ACTION_ATTACK:
                        sNoEffect = self._min(gm, board, state, alpha, beta, depth + 1, maxRoundDepth, other)

                        # action have effect
                        s1, _ = gm.activate(board, state, action, True)
                        sEffect = evaluateState(self.boardValues, s1)
                        pEffect = probabilityOfSuccessfulAttack(gm, board, state, action)

                        # effect of action with enemy response killing the unit
                        s2, _ = gm.activate(board, state, action)
                        s2.getFigure(action).killed = True
                        sRespEffect = evaluateState(self.boardValues, s2)

                        # accumulated probability of a successful response
                        pRespEffect = probabilityOfSuccessfulResponseAccumulated(gm, board, state, action)

                        score = pEffect * sEffect + (1 - pEffect) * (
                                    pRespEffect * sRespEffect + (1 - pRespEffect) * sNoEffect)

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        startTime = time.time()
        val = -1
        bestAction = None

        for currentDepth in range(1, self.maxDepth + 1):

            if time.time() - startTime > self.maxSearchtime:
                break

            if self.team == RED:
                score, action, winner = self._max(gm, board, state, -math.inf, math.inf, 0, currentDepth, self.team)
            else:
                score, action, winner = self._min(gm, board, state, -math.inf, math.inf, 0, currentDepth, self.team)

            if winner:
                bestAction = action
                break
            if score > val:
                val = score
                bestAction = action

        return bestAction
