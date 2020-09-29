import logging
import math

from agents import Agent, MatchManager, GreedyAgent
from agents.commons import stateScore
from core import GM
from core.actions import Action
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import GoalParams
from core.game.state import GameState
from utils.copy import deepcopy

logger = logging.getLogger()


class ABPuppet(Agent):
    """This is just a "puppet", a fake-agent that answer always with the same action/response, that can be changed."""

    def __init__(self, team: str):
        super().__init__('puppet', team)

        self.action: Action or None = None
        self.response: Action or None = None

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        return self.action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        return self.response


class AlphaBetaAgent(Agent):

    def __init__(self, team: str, maxDepth: int = 3):
        super().__init__('AlphaBetaAgent', team)

        self.maxDepth: int = maxDepth
        self.cache: dict = {}
        self.goal_params: GoalParams = GoalParams()

        self.puppets = {RED: ABPuppet(RED), BLUE: ABPuppet(BLUE)}
        self.mm = MatchManager('', self.puppets[RED], self.puppets[BLUE])

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
            score = stateScore(self.team, self.goal_params, board, state)
            self.cache[hash(state)] = score
            return score, None

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
            score, _ = self.alpha_beta(board, s, -math.inf, math.inf, self.maxDepth)

            if score > max_value:
                max_value = score
                max_color = color

        state.choose(self.team, max_color)
        logging.info(f'{self.team:5}: choose positions color {max_color}')
