import logging
import math

from agents import GreedyAgent
from core import GM
from core.actions import Action
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import goalAchieved
from core.game.state import GameState


class AlphaBetaAgent(GreedyAgent):

    def __init__(self, team: str, maxDepth: int = 1):
        super().__init__(team)

        self.maxDepth: int = maxDepth
        self.cache: dict = {}

    def stateScore(self, board: GameBoard, state: GameState) -> float:
        goals = board.getObjectives(self.team)
        return sum([goal.score(state) for goal in goals])

    def alpha_beta(self, board: GameBoard, state: GameState, alpha, beta, depth, team, response):
        stateHash = hash(state)
        if stateHash in self.cache:
            return self.cache[stateHash], None

        if not response:
            # check for an update
            reds = state.getFiguresCanBeActivated(RED)
            blues = state.getFiguresCanBeActivated(BLUE)

            if len(reds) == 0 and len(blues) == 0:
                GM.update(state)

        end, _ = goalAchieved(board, state)

        if depth == 0 or end:
            score = self.stateScore(board, state)
            self.cache[hash(state)] = score
            return score, None

        # what will be the reaction from other player
        if team == RED:
            otherTeam, otherResponse = (RED, False) if response else (BLUE, True)
        else:
            otherTeam, otherResponse = (BLUE, False) if response else (RED, True)

        nextActions = []

        for figure in state.getFiguresCanBeActivated(team):
            nextActions.append(GM.actionPass(figure))

            if response:
                nextActions += GM.buildResponses(board, state, figure)
            else:
                # standard actions
                nextActions += GM.buildAttacks(board, state, figure)
                nextActions += GM.buildMovements(board, state, figure)

        # RED maximize...
        if team == RED:
            value = -math.inf
            action = None
            for action in nextActions:
                s1, _ = GM.activate(board, state, action)
                score, _ = self.alpha_beta(board, s1, depth - 1, alpha, beta, otherTeam, otherResponse)

                if score > value:
                    value, action = score, action
                    logging.info(f'AB: Max {action} [{score}]')

                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, action

        # ...BLUE minimize
        else:
            value = math.inf
            action = None
            for action in nextActions:
                s1, _ = GM.activate(board, state, action)
                score, _ = self.alpha_beta(board, s1, depth - 1, alpha, beta, otherTeam, otherResponse)

                if score < value:
                    value, action = score, action
                    logging.info(f'AB: Min {action} [{score}]')

                beta = min(beta, value)
                if beta <= alpha:
                    break

            return value, action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        score, action = self.alpha_beta(board, state, -math.inf, math.inf, self.maxDepth, self.team, False)

        if not action:
            raise ValueError('no action given')

        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        score, action = self.alpha_beta(board, state, -math.inf, math.inf, self.maxDepth, self.team, True)

        if not action:
            raise ValueError('no response given')

        return action
