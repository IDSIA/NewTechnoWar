"""This agent is an adaptation from the GreedyAgent in the main project source code."""
import logging
import math
from typing import Tuple, List

import numpy as np

from agents import Agent
from agents.commons import stateScore
from agents.utils import entropy, standardD
from core.actions import Action, Attack, Response
from core.figures import Figure
from core.game import GameBoard, GameState, GoalParams
from core.utils.coordinates import Hex
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class GreedyAgent(Agent):

    def __init__(self, team: str, maximize: bool = True, seed: int = 0):
        """
        :param team:        color of the team
        :param maximize:    if true optimize for maximize the score, otherwise to minimize
        :param seed:        random seed to use internally
        """
        super().__init__('GreedyAgent', team, seed=seed)

        self.goal_params: GoalParams = GoalParams()
        self.maximize: bool = maximize

    def dataFrameInfo(self) -> List[str]:
        """
        The additional columns are:
            - score:    score associated with the chosen action
            - action:   action performed
            - entropy:  entropy valued associated with the chosen action
            - n_scores: number of available actions
            - scores:   scores for all the available actions
            - actions:  all the available actions

        :return: a list with the name of the columns used in the dataframe
        """
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'standard_deviation', 'n_scores', 'scores', 'actions'
        ]

    def store(self, state: GameState, bestScore: float, bestAction: Action,
              scoreActions: List[Tuple[float, Action]]) -> None:
        """
        Wrapper of the register() method that does some pre-processing on the data that will be saved.

        :param state:           state of the game
        :param bestScore:       score of the best action found
        :param bestAction:      best action found
        :param scoreActions:    list of all actions with their score
        """
        scores = [x[0] for x in scoreActions]
        actions = [type(x[1]).__name__ for x in scoreActions]

        data = [bestScore, type(bestAction).__name__, entropy(scores), standardD(scores), len(scoreActions), scores,
                actions]

        self.register(state, data)

    def evaluateState(self, board: GameBoard, state: GameState, action: Action, baseScore: float = 0) -> float:
        """
        Activates the given action and then uses the stateScore() function to evaluate and assign a score to the given
        state of the game. The score for an attack Action are smoothed with the probability of success.

        :param board:       board of the game
        :param state:       current state of the game
        :param action:      action to perform
        :param baseScore:   adjustment score for attack actions
        :return:
        """
        s1, outcome = self.gm.activate(board, state, action)
        score = stateScore(self.team, self.goal_params, board, s1)

        if isinstance(action, Attack):
            w = min(1.0, (outcome.hitScore - 1) / 19)
            score = w * score + (1 - w) * baseScore

        return score

    def scorePass(self, board: GameBoard, state: GameState, figure: Figure = None) -> List[Tuple[float, Action]]:
        """
        If the figure is given, compute the score for the PassFigure action; otherwise compute the score for the
        PassTeam action.

        :param board:       board of the game
        :param state:       current state of the game
        :param figure:      figure that will perform the action
        :return: a list with one element composed by the score and the action
        """
        if figure:
            action = self.gm.actionPassFigure(figure)
        else:
            action = self.gm.actionPassTeam(self.team)
        score = self.evaluateState(board, state, action)
        return [(score, action)]

    def scoreMove(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        """
        :param board:       board of the game
        :param state:       current state of the game
        :param figure:      figure that will perform the action
        :return: a list with all the move actions for the given figure and their score
        """
        scores = []
        for action in self.gm.buildMovements(board, state, figure):
            score = self.evaluateState(board, state, action)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current move score is {score}')

        return scores

    def scoreAttack(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        """
        :param board:       board of the game
        :param state:       current state of the game
        :param figure:      figure that will perform the action
        :return: a list with all the attack actions for the given figure and their score
        """
        baseScore = stateScore(self.team, self.goal_params, board, state)
        scores = []

        for action in self.gm.buildAttacks(board, state, figure):
            score = self.evaluateState(board, state, action, baseScore)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current attack score is {score}')

        return scores

    def scoreResponse(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        """
        :param board:       board of the game
        :param state:       current state of the game
        :param figure:      figure that will perform the action
        :return: a list with all the responses for the given figure and their score
        """
        baseScore = stateScore(self.team, self.goal_params, board, state)
        scores = []

        responses = [self.gm.actionNoResponse(self.team)] + self.gm.buildResponses(board, state, figure)

        for action in responses:
            score = self.evaluateState(board, state, action, baseScore)
            scores.append((score, action))

            logger.debug(f'{self.team:5}: Current response score is {score}')

        return scores

    def opt(self, scores) -> Tuple[float, Action or Response]:
        """
        Optimization function based on the init parameter maximize.

        :param scores:  list of all the possible actions, or responses, with their score
        :return: the optimal score and action
        """
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
        """
        Choose the best action based on the defined heuristic and optimization function.

        :param board:   board of the game
        :param state:   the current state
        :return: the next action to apply
        """
        scores = []

        # compute all scores for possible actions for each available unit
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scorePass(board, state, figure)
            scores += self.scoreMove(board, state, figure)
            scores += self.scoreAttack(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)

        self.store(state, score, action, scores)

        logger.debug(f'{self.team:5}: {action} ({score})')
        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        """
        Choose the best response based on the defined heuristic and optimization function.

        :param board:   board of the game
        :param state:   the current state
        :return: the next response to apply
        """
        scores = [] + self.scorePass(board, state)

        # compute all scores for possible responses
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scoreResponse(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)

        self.store(state, score, action, scores)

        logger.debug(f'{self.team:5}: {action} ({score})')
        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """
        Find the initial position for the figure where the state has the best value. The generation of the position is
        done randomly 100 times.

        :param board:   board of the game
        :param state:   the current state
        """
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
        """
        Find the best color that gives the optimal score.

        :param board:   board of the game
        :param state:   the current state
        """
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
