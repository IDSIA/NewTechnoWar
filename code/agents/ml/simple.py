from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState
from agents import Agent, GreedyAgent
import numpy as np
from core.const import RED, BLUE
import pandas as pd
import os.path as op
import random

import joblib
from scipy.stats import entropy

dir_path = op.dirname(op.realpath(__file__))


class SimpleMLAgent(Agent):

    def __init__(self, team: str, params: dict):

        super().__init__('SimpleML', team)

        # file = params['scenario'] + '_' + params['model'] + '.joblib'
        file = params['scenario'] + '_' + params['model'] + '_' + params['color'] + '.joblib'
        self.vectors = []
        self.randomChoice = False
        self.set = 0
        self.count = 0
        self.params: dict = params
        # self.model = joblib.load(op.join(dir_path, '..', '..', 'models', file))
        self.model = joblib.load(op.join(dir_path, '..', '..', 'modelsRegressor', file))

    def dfColor(self, df, color):
        df_new = df[[c for c in df.columns if color in c]]
        return df_new

    def takeProbs(self, scores: list):
        probabilieties = []
        if self.team == BLUE:
            i = 0
        else:
            i = 1
        for probs, action in scores:
            probabilieties.append(probs[0])
        arr = np.array(probabilieties)
        return arr[:, i]  # prima o seconda colonna in base all'agente se rosso o blu

    def entropyClassiefier(self, scores: list):
        probs = self.takeProbs(scores)
        norm = [float(i) / sum(probs) for i in probs]
        return -(norm * np.log(norm) / np.log(len(scores))).sum()
        # ritorna il valore di entropia di tutte le probabilità

    def createDf_info(self):
        info = ["Agente", "Probabilità", "Mossa", "Entropia", "Mosse disponibili", "RandomChoice", "SceltaRandom",
                "Count"]
        return info

    def vectorDf(self, bestscore, bestaction, scores):

        data = [self.team, bestscore, bestaction, self.entropyClassiefier(scores), len(scores), self.randomChoice,
                self.set, self.count]
        self.count += 1
        return data

    def createDf(self, numero):
        cols = self.createDf_info()

        df = pd.DataFrame(data=self.vectors, columns=cols)
        repeated = [numero] * len(df)
        df["Numero Partita"] = repeated
        return df

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

    def bestActionRandom(self, scores: list) -> Action:
        self.set = 10
        bestScore, bestAction = 0.0, None
        if len(scores) != 0:
            sorted_multi_list = sorted(scores, key=lambda x: x[0][0][0])
            # questo sorted mi occupa moooolto tempo, si può fare altro modo?
            if self.team == BLUE:
                choice = random.choice(sorted_multi_list[-self.set:])
                bestScore = choice[0][0][0]
                bestAction = choice[1]
            else:
                choice = random.choice(sorted_multi_list[:self.set])
                bestScore = choice[0][0][1]
                bestAction = choice[1]
        return bestScore, bestAction

    def bestScore(self,scores: list):
        bestScore, bestAction = 0.0, None

        for probs, action in scores:
            if probs >= bestScore:
                bestScore, bestAction = probs, action

        return bestScore, bestAction

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)
            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                X = np.array(newState.vector()).reshape(1, -1)
                cols = newState.vectorInfo()
                df = pd.DataFrame(data=X, columns=cols)
                df = self.dfColor(df, self.team)

                # score = self.model.predict_proba(df)
                score = self.model.predict(df)

                scores.append((score, action))
        '''if self.randomChoice:
            bestscore, bestaction = self.bestActionRandom(scores)
        else:
            bestscore, bestaction = self.bestAction(scores)'''
        bestscore, bestaction = self.bestScore(scores)
        # v = self.vectorDf(bestscore, bestaction, scores)
        # self.vectors.append(v)
        if not bestaction:
            raise ValueError('No action given')

        # v = list(self.vectorDf(bestscore, bestaction, scores))
        # self.vectors.append(v)

        return bestaction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:

        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassResponse(self.team)] + \
                      GM.buildResponses(board, state, figure)
            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                X = np.array(newState.vector()).reshape(1, -1)
                cols = newState.vectorInfo()
                df = pd.DataFrame(data=X, columns=cols)
                df = self.dfColor(df, self.team)

                # score = self.model.predict_proba(df)
                score = self.model.predict(df)
                scores.append((score, action))
        '''if self.randomChoice:
            bestscore, bestaction = self.bestActionRandom(scores)
        else:
            bestscore, bestaction = self.bestAction(scores)
        if bestaction is not None:
            v = self.vectorDf(bestscore, bestaction, scores)
            self.vectors.append(v)'''
        bestscore, bestaction = self.bestScore(scores)
        if not bestaction:
            raise ValueError('No action given')
        return bestaction

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea?
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea? now random
        colors = list(state.choices[self.team].keys())
        color = np.random.choice(colors)

        state.choose(self.team, color)
