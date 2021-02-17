import logging
import os
from typing import List, Tuple

import joblib
import numpy as np
import pandas as pd

from agents import Agent, GreedyAgent
from agents.utils import entropy
from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState


class MLAgent(Agent):

    def __init__(self, name: str, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__(name, team, seed)

        self.filename = filename
        self.model = joblib.load(os.path.join(os.getcwd(), filename))

        self.randomChoice = randomChoice

        self.set = 0

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'n_scores', 'scores', 'actions', 'random_choice', 'n_choices'
        ]

    def store(self, state: GameState, bestScore: float, bestAction: Action, actionsScores: list):
        scores = [i[0] for i in actionsScores]
        actions = [type(i[1]).__name__ for i in actionsScores]

        data = [
            bestScore, type(bestAction).__name__, entropy(scores), len(scores), scores, actions, self.randomChoice,
            self.set
        ]

        self.register(state, data)

    def scores(self, state: GameState, stateActions: List[Action]) -> List[Tuple[float, Action]]:
        raise NotImplemented()

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
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)

            all_actions += actions

        if not all_actions:
            raise ValueError('No action given')

        scores = self.scores(state, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        self.store(state, bestScore, bestAction, scores)

        if not bestAction:
            raise ValueError('No action given')

        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        all_actions = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassResponse(self.team)] + \
                      GM.buildResponses(board, state, figure)

            all_actions += actions

        if not all_actions:
            raise ValueError('No response given')

        scores = self.scores(state, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        if not bestAction:
            raise ValueError('No response given')

        self.store(state, bestScore, bestAction, scores)

        logging.debug(f'BEST RESPONSE {self.team:5}: {bestAction} ({bestScore})')

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
