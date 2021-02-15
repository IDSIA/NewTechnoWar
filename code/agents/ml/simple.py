import os.path as op
import random

import joblib
import numpy as np
import pandas as pd

from agents import Agent, GreedyAgent
from core import GM
from core.actions import Action
from core.const import BLUE
from core.game.board import GameBoard
from core.game.state import GameState

dir_path = op.dirname(op.realpath(__file__))


class SimpleMLAgent(Agent):

    def __init__(self, team: str, params: dict, randomChoice=False, seed=0):
        super().__init__('SimpleML', team, seed)

        file = params['scenario'] + '_' + params['model'] + '.joblib'
        self.randomChoice = randomChoice

        self.set = 0

        self.params: dict = params
        self.model = joblib.load(op.join(dir_path, '..', '..', 'models', file))

    def takeProbs(self, scores: list):
        probabilities = []
        i = 0 if self.team == BLUE else 1

        for probs, action in scores:
            probabilities.append(probs[0])

        arr = np.array(probabilities)
        return arr[:, i]  # first column red, second column blue agent

    def entropy(self, scores: list):
        # TODO: change with entropy in utils
        probs = self.takeProbs(scores)
        if any(probs):
            norm = [float(i) / sum(probs) for i in probs]
            return -(norm * np.log(norm) / np.log(len(scores))).sum()
        else:
            return 0

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'n_scores', 'scores', 'random_choice', 'set'
        ]

    def store(self, bestScore, bestAction, scores):
        # TODO: register type of actions
        data = [bestScore, bestAction, self.entropy(scores), len(scores), scores, self.randomChoice, self.set]

        self.register(data)

    def createDf(self):
        return pd.DataFrame(data=self.history, columns=self.dataFrameInfo())

    def bestAction(self, scores: list):
        bestScore, bestAction = 0.0, None
        for probs, action in scores:
            if self.team == BLUE:
                score = probs[0, 0]
            else:
                score = probs[0, 1]
            if score >= bestScore:
                bestScore, bestAction = score, action

        return bestScore, bestAction

    def bestActionRandom(self, scores: list) -> (float, Action):
        self.set = 10
        bestScore, bestAction = 0.0, None
        if len(scores) > 0:
            sorted_multi_list = sorted(scores, key=lambda x: x[0][0][0])
            # TODO questo sorted mi occupa moooolto tempo, si può fare altro modo?
            if self.team == BLUE:
                choice = random.choice(sorted_multi_list[-self.set:])
                bestScore = choice[0][0][0]
                bestAction = choice[1]
            else:
                choice = random.choice(sorted_multi_list[:self.set])
                bestScore = choice[0][0][1]
                bestAction = choice[1]
        return bestScore, bestAction

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)
            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                X = np.array(newState.vectorState()).reshape(1, -1)
                cols = newState.vectorStateInfo()
                df = pd.DataFrame(data=X, columns=cols)
                score = self.model.predict_proba(df)

                scores.append((score, action))
        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        self.store(bestScore, bestAction, scores)

        if not bestAction:
            raise ValueError('No action given')

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
                score = self.model.predict_proba(df)
                scores.append((score, action))

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        if bestAction is not None:
            self.store(bestScore, bestAction, scores)

        if not bestAction:
            raise ValueError('No action given')

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
