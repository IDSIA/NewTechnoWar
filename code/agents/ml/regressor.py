from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState
from agents import Agent, GreedyAgent
import numpy as np
import pandas as pd
import os.path as op
import random
import logging
import joblib

dir_path = op.dirname(op.realpath(__file__))


class RegressorAgent(Agent):

    def __init__(self, team: str, params: dict):

        super().__init__('Regressor', team)

        file = params['scenario'] + '_' + params['model'] + '_' + params['color'] + '.joblib'
        self.vectors = []
        self.randomChoice = False
        self.set = 0
        self.count = 0
        self.params: dict = params
        self.model = joblib.load(op.join(dir_path, '..', '..', 'modelsRegressor', file))

    def entropy(self, scores: list):
        probs = [i[0][0] for i in scores]
        res = [ele for ele in probs if ele > 0]
        if len(res) > 1:
            norm = [float(i) / sum(res) for i in res]
            return -(norm * np.log(norm) / np.log(len(res))).sum()
        else:
            return 0
        # ritorna il valore di entropia di tutte le probabilità

    def createDf_info(self):
        info = ["Agente", "Score", "Mossa", "Entropia", "Mosse disponibili", "Scores", "TipoMossa" ,"RandomChoice",
                "SceltaRandom", "Count"]
        return info

    def vectorDf(self, bestscore, bestaction, scores):
        a = [i[0][0] for i in scores]
        b = [type(i[1]).__name__ for i in scores]

        data = [self.team, bestscore[0], bestaction, self.entropy(scores), len(scores), a, b, self.randomChoice,
                self.set, self.count]
        self.count += 1
        return data

    def createDf(self, numero):
        cols = self.createDf_info()

        df = pd.DataFrame(data=self.vectors, columns=cols)
        repeated = [numero] * len(df)
        df["Numero Partita"] = repeated
        return df

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

    def bestScoreRandom(self, scores: list) -> Action:
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

                X = np.array(newState.vector()).reshape(1, -1)
                cols = newState.vectorInfo()
                df = pd.DataFrame(data=X, columns=cols)
                df = self.dfColor(df, self.team)

                # score = self.model.predict_proba(df)
                score = self.model.predict(df)

                scores.append((score, action))

        if self.randomChoice:
            bestscore, bestaction = self.bestScoreRandom(scores)
        else:
            bestscore, bestaction = self.bestScore(scores)

        v = self.vectorDf(bestscore, bestaction, scores)
        self.vectors.append(v)
        if not bestaction:
            raise ValueError('No action given')

        v = list(self.vectorDf(bestscore, bestaction, scores))
        self.vectors.append(v)
        logging.info(f'BEST ACTION {self.team:5}: {bestaction} ({bestscore})')
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
                score = self.model.predict(df)
                scores.append((score, action))

        if self.randomChoice:
            bestscore, bestaction = self.bestScoreRandom(scores)
        else:
            bestscore, bestaction = self.bestScore(scores)
        if bestaction is not None:
            v = self.vectorDf(bestscore, bestaction, scores)
            self.vectors.append(v)
        if not bestaction:
            raise ValueError('No action given')
        logging.info(f'BEST RESPONSE {self.team:5}: {bestaction} ({bestscore})')

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
