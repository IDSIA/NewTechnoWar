import logging
import os
from typing import List, Tuple

import joblib
import numpy as np

from agents import Agent, GreedyAgent
from agents.utils import entropy
from core.actions import Action
from core.game import GameBoard, GameState

logger = logging.getLogger(__name__)


class MLAgent(Agent):

    def __init__(self, name: str, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__(name, team, seed)

        self.filename = filename
        self.model = joblib.load(os.path.join(os.getcwd(), filename))
        # TODO qui vorrei caricare il modello in base al tipo di azione

        self.randomChoice = None

        self.set = 0

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'n_scores', 'scores', 'actions', 'random_choice', 'n_choices'
        ]

    def store(self, state: GameState, bestScore: float, bestAction: Action, actionsScores: list):
        scores = [i[0] for i in actionsScores]
        actions = [type(i[1]).__name__ for i in actionsScores]

        h = entropy(scores)

        if h > 1. or h < 0.:
            logger.warning(f'Entropy out of range: {h}')
            logger.warning(f'{scores}')

        data = [bestScore, type(bestAction).__name__, h, len(scores), scores, actions, self.randomChoice, self.set]

        self.register(state, data)

    def scores(self, state: GameState, board: GameBoard, stateActions: List[Action]) -> List[Tuple[float, Action]]:
        raise NotImplemented()

    # forces you to implement it, as it will throw an exception when you try to run it until you do so.

    @staticmethod
    def bestAction(scores: List[Tuple[float, Action]]):
        bestScore, bestAction = -1e9, None
        for score, action in scores:
            if score >= bestScore:
                bestScore, bestAction = score, action

        return bestScore, bestAction

    def bestActionRandom(self, scores: List[Tuple[float, Action]]) -> (float, Action):
        self.set = 10
        bestScore, bestAction = 0.0, None
        if len(scores) > 0:
            sorted_multi_list = sorted(scores, key=lambda x: x[0])
            choice = np.random.randint(0, max(self.set, len(scores)))
            bestScore, bestAction = sorted_multi_list[:self.set][choice]
        return bestScore, bestAction

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        all_actions = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [self.gm.actionPassFigure(figure)] + \
                      self.gm.buildAttacks(board, state, figure) + \
                      self.gm.buildMovements(board, state, figure)

            all_actions += actions

        if not all_actions:
            logger.warning('No actions available: no action given')
            raise ValueError('No action given')

        scores = self.scores(state, board, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        self.store(state, bestScore, bestAction, scores)

        if not bestAction:
            logger.warning('No best action found: no action given')
            raise ValueError('No action given')

        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        all_actions = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [self.gm.actionPassResponse(self.team)] + \
                      self.gm.buildResponses(board, state, figure)

            all_actions += actions

        if not all_actions:
            logger.warning('No actions available: no response given')
            raise ValueError('No response given')

        scores = self.scores(state, board, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        if not bestAction:
            logger.warning('No best action found: no response given')
            raise ValueError('No response given')

        self.store(state, bestScore, bestAction, scores)

        logger.debug(f'BEST RESPONSE {self.team:5}: {bestAction} ({bestScore})')

        return bestAction

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea?
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea? now random
        colors = list(state.choices[self.team].keys())
        color = np.random.choice(colors)

        state.choose(self.team, color)
