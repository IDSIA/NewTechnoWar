"""This agent is an adaptation from the GreedyAgent in the main project source code."""
import logging
import math
from typing import Tuple, Any, List

import numpy as np

from agents import Agent
from agents.commons import stateScore
from agents.utils import entropy, standardD
from core.actions import Action
from core.figures import Figure
from core.game import GameBoard, GameState, GoalParams
from core.utils.coordinates import Hex
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class GreedyAgent(Agent):

    def __init__(self, team: str, seed=0):
        super().__init__('GreedyAgent', team, seed=seed)

        self.goal_params: GoalParams = GoalParams()
        self.maximize: bool = True

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'standard_deviation', 'n_scores', 'scores', 'actions'
        ]

    def store(self, state: GameState, bestScore: float, bestAction: Action, scoreActions: list, board: GameBoard):
        scores = [x[0] for x in scoreActions]
        actions = [type(x[1]).__name__ for x in scoreActions]

        data = [bestScore, type(bestAction).__name__, entropy(scores), standardD(scores), len(scoreActions), scores,
                actions] 

        self.register(state, data)

    def evaluateState(self, board: GameBoard, state: GameState, action: Action, baseScore: float = 0) -> float:
        s1, outcome = self.gm.activate(board, state, action)
        score = stateScore(self.team, self.goal_params, board, s1)

        if 'hitScore' in outcome:
            w = (outcome['hitScore'] - 1) / 19
            score = w * score + (1 - w) * baseScore

        return score

    def scorePass(self, board: GameBoard, state: GameState, figure: Figure = None) -> List[Tuple[float, Action]]:
        if figure:
            action = self.gm.actionPassFigure(figure)
        else:
            action = self.gm.actionPassTeam(self.team)
        score = self.evaluateState(board, state, action)
        return [(score, action)]

    def scoreMove(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        scores = []
        for action in self.gm.buildMovements(board, state, figure):
            score = self.evaluateState(board, state, action)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current move score is {score}')

        return scores

    def scoreAttack(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        baseScore = stateScore(self.team, self.goal_params, board, state)
        scores = []

        for action in self.gm.buildAttacks(board, state, figure):
            score = self.evaluateState(board, state, action, baseScore)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current attack score is {score}')

        return scores

    def scoreResponse(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        baseScore = stateScore(self.team, self.goal_params, board, state)
        scores = []

        responses = [self.gm.actionPassResponse(self.team)] + self.gm.buildResponses(board, state, figure)

        for action in responses:
            score = self.evaluateState(board, state, action, baseScore)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current response score is {score}')

        return scores

    def opt(self, scores) -> Tuple[float, Any]:
        max_value = -math.inf
        min_value = math.inf
        max_action = None
        min_action = None

        # search for best score
        for score, action in scores:
            if score > max_value:
                max_value = score
                max_action = action
            if score < min_value:
                min_value = score
                min_action = action

        if self.maximize:
            return max_value, max_action
        return min_value, min_action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        # compute all scores for possible actions for each available unit
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scorePass(board, state, figure)
            scores += self.scoreMove(board, state, figure)
            scores += self.scoreAttack(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)

        self.store(state, score, action, scores, board)

        logger.debug(f'{self.team:5}: {action} ({score})')
        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:

        scores = [] + self.scorePass(board, state)

        # compute all scores for possible responses
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scoreResponse(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)

        self.store(state, score, action, scores, board)

        logger.debug(f'{self.team:5}: {action} ({score})')
        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # select area
        x, y = np.where(state.placement_zone[self.team] > 0)
        figures = state.getFigures(self.team)

        # choose groups of random positions
        indices = [np.random.choice(len(x), size=len(figures), replace=False) for _ in range(100)]

        scores = []
        s = deepcopy(state)

        for i in range(len(indices)):
            # select a group of positions
            group = indices[i]
            for j in range(len(group)):
                # move each unit to its position
                figure = figures[j]
                dst = Hex(x[group[j]], y[group[j]]).cube()
                s.moveFigure(figure, figure.position, dst)

            score = stateScore(self.team, self.goal_params, board, s)
            scores.append((score, group))

        # choose the better group
        score, group = self.opt(scores)

        for j in range(len(group)):
            figure = figures[j]
            dst = Hex(x[group[j]], y[group[j]]).cube()
            state.moveFigure(figure, dst=dst)

        logger.info(f'{self.team:5}: placed his troops in {group} ({score})')

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        colors = list(state.choices[self.team].keys())
        scores = []

        for color in colors:
            s = deepcopy(state)
            s.choose(self.team, color)

            score = stateScore(self.team, self.goal_params, board, s)
            scores.append((score, color))

        score, color = self.opt(scores)
        state.choose(self.team, color)

        logger.info(f'{self.team:5}: choose positions color {color}')
