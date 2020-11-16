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

        file = params['scenario'] + '_' + params['model'] + '.joblib'

        self.params: dict = params
        self.model = joblib.load(op.join(dir_path, '..', '..', 'models', file))

    def bestAction(self, scores: list) -> Action:
        entropies=[]
        bestScore, bestAction = 0.0, None
        print(sorted(scores, reverse=True))

        for probs, action in scores:
            entropies.append(entropy(probs[0],base=len(scores)))
            if (self.team == BLUE):
                score = probs[0, 0]
            else:
                score = probs[0, 1]
            if score >= bestScore:
                bestScore, bestAction = score, action

        return bestAction

    def bestActionRandom(self, scores: list) -> Action:
        bestAction=None
        if(len(scores)!=0):
            sorted_multi_list = sorted(scores, key=lambda x: x[0][0][0])
            #questo sorted mi occupa moooolto tempo, si può fare altro modo?
            if (self.team == BLUE):
                bestAction = random.choice(sorted_multi_list[-10:])[1]
            else:
                bestAction = random.choice(sorted_multi_list[:10])[1]
        return bestAction

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
                score = self.model.predict_proba(df)

                scores.append((score, action))
        bestaction = self.bestActionRandom(scores)
        if not bestaction:
            raise ValueError('No action given')
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
                score = self.model.predict_proba(df)
                scores.append((score, action))
        bestaction = self.bestActionRandom(scores)
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
