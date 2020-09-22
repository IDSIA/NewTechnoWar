import logging
import math

from agents import Player, MatchManager
from core import GM
from core.actions import Action
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import GoalParams
from core.game.state import GameState

logger = logging.getLogger()


class ABPuppet(Player):
    """This is just a "puppet", a fake-agent that answer always with the same action/response, that can be changed."""

    def __init__(self, team: str):
        super().__init__('puppet', team)

        self.action: Action or None = None
        self.response: Action or None = None

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        return self.action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        return self.response


class AlphaBetaAgent(Player):

    def __init__(self, team: str, maxDepth: int = 3):
        super().__init__('AlphaBetaAgent', team)

        self.maxDepth: int = maxDepth
        self.cache: dict = {}
        self.goal_params: GoalParams = GoalParams()

        self.puppets = {RED: ABPuppet(RED), BLUE: ABPuppet(BLUE)}
        self.mm = MatchManager('', self.puppets[RED], self.puppets[BLUE])

    def stateScore(self, board: GameBoard, state: GameState) -> float:
        goals = board.getObjectives(self.team)
        return sum([goal.score(state, self.goal_params) for goal in goals])

    def alpha_beta(self, board: GameBoard, state: GameState, alpha, beta, depth):
        stateHash = hash(state)
        if stateHash in self.cache and self.maxDepth != depth:
            return self.cache[stateHash], None

        self.mm.loadState(board, state)
        step, team, _ = self.mm.nextPlayer()

        if step == 'update':
            self.mm.step()
            step, team, _ = self.mm.nextPlayer()

        if depth == 0 or step == 'end' or team == '':
            score = self.stateScore(board, state)
            self.cache[hash(state)] = score
            return score, None

        nextActions = []

        if step == 'response':
            nextActions.append(GM.actionPassResponse(team))
            for figure in state.getFiguresCanRespond(team):
                nextActions += GM.buildResponses(board, state, figure)
        else:
            for figure in state.getFiguresCanBeActivated(team):
                nextActions.append(GM.actionPass(figure))

                # standard actions
                nextActions += GM.buildAttacks(board, state, figure)
                nextActions += GM.buildMovements(board, state, figure)

        # this team maximize...
        if team == self.team:
            value = -math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                s1, _ = GM.activate(board, state, nextAction)
                score, _ = self.alpha_beta(board, s1, alpha, beta, depth - 1)

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
                score, _ = self.alpha_beta(board, s1, alpha, beta, depth - 1)

                if score < value:
                    value, action = score, nextAction
                    logging.debug(f'       AB{depth}: Min {action} [{score}]')

                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value, action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        # TODO: find a better log management...
        logger.disabled = True

        score, action = self.alpha_beta(board, state, -math.inf, math.inf, self.maxDepth)

        logger.disabled = False

        if not action:
            raise ValueError('no action given')

        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        # TODO: find a better log management...
        logger.disabled = True

        score, action = self.alpha_beta(board, state, -math.inf, math.inf, self.maxDepth)

        logger.disabled = False

        if not action:
            raise ValueError('no response given')

        return action
