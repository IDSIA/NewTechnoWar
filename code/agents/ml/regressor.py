import logging
import os.path as op
import random

import joblib
import numpy as np
import pandas as pd

from agents import Agent, GreedyAgent
from agents.utils import entropy
from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState, vectorState, vectorStateInfo

dir_path = op.dirname(op.realpath(__file__))


class RegressorAgent(Agent):

    def __init__(self, team: str, params: dict, randomChoice=False, seed=0):
        super().__init__('Regressor', team, seed)

        file = params['scenario'] + '_' + params['model'] + '_' + team + '.joblib'
        self.randomChoice = randomChoice

        self.params: dict = params
        self.model = joblib.load(op.join(dir_path, '..', '..', 'models', file))

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'n_scores', 'scores', 'actions', 'random_choice'
        ]

    def store(self, bestScore, bestAction, scores):
        # TODO: check this
        probs = [i[0][0] for i in scores]
        actions = [type(i[1]).__name__ for i in scores]

        res = [ele for ele in probs if ele > 0]

        data = [bestScore[0], bestAction, entropy(res), len(scores), probs, actions, self.randomChoice]

        self.register(data)

    def bestScore(self, scores: list):
        # bestScore, bestAction = 0.0, None
        if any(scores):
            bestScore = scores[0][0][0]
            bestAction = scores[0][1]
        else:
            bestScore, bestAction = 0.0, None

        for probs, action in scores:
            if probs >= bestScore:
                bestScore, bestAction = probs, action
        return bestScore, bestAction

    def bestScoreRandom(self, scores: list):
        set1 = 10
        bestScore, bestAction = 0.0, None
        if len(scores) != 0:
            sorted_multi_list = sorted(scores, key=lambda x: x[0][0])
            # questo sorted mi occupa moooolto tempo, si può fare altro modo?
            choice = random.choice(sorted_multi_list[:set1])
            bestScore = choice[0][0]
            bestAction = choice[1]

        return bestScore, bestAction

    def dfColor(self, df, color):
        df_new = df[[c for c in df.columns if color in c]]
        return df_new

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)
            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                X = np.array(vectorState(newState)).reshape(1, -1)
                df = pd.DataFrame(data=X, columns=vectorStateInfo())
                df = self.dfColor(df, self.team)

                score = self.model.predict(df)
                scores.append((score, action))

        if self.randomChoice:
            bestScore, bestAction = self.bestScoreRandom(scores)
        else:
            bestScore, bestAction = self.bestScore(scores)

        self.store(bestScore, bestAction, scores)

        if not bestAction:
            raise ValueError('No action given')

        logging.debug(f'BEST ACTION {self.team:5}: {bestAction} ({bestScore})')
        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassResponse(self.team)] + \
                      GM.buildResponses(board, state, figure)
            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                X = np.array(newState.vectorState()).reshape(1, -1)
                cols = newState.vectorStateInfo()
                df = pd.DataFrame(data=X, columns=cols)
                df = self.dfColor(df, self.team)

                score = self.model.predict(df)
                scores.append((score, action))

        if self.randomChoice:
            bestScore, bestAction = self.bestScoreRandom(scores)
        else:
            bestScore, bestAction = self.bestScore(scores)

        if bestAction is not None:
            self.store(bestScore, bestAction, scores)

        if not bestAction:
            raise ValueError('No action given')

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
