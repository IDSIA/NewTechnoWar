from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState
from agents import Agent, GreedyAgent
import numpy as np
from core.const import RED, BLUE
import pandas as pd
import os.path as op

import joblib

dir_path = op.dirname(op.realpath(__file__))


class SimpleMLAgent(Agent):

    def __init__(self, team: str, params: dict):
        super().__init__('SimpleML', team)

        file = params['scenario'] + '_' + params['model'] + '.joblib'

        self.params: dict = params
        self.model = joblib.load(op.join(dir_path, '..', '..', 'models', file))
        # TODO: assolutamente gestire meglio il percorso

    def bestAction(self, scores: list) -> Action:
        bestScore, bestAction = 0.0, None
        for probs, action in scores:
            if (self.team == BLUE):
                score = probs[0]
            else:
                score = probs[1]
            if score >= bestScore:
                bestScore, bestAction = score, action
                # sarà qui che devo già selezionare lo score del giocatore, se si tratta del blue o del rosso

                # devo usare team? stile if self.team== red allora else altro?
        # print("oh", score)
        # print("ehi", bestAction)
        return bestAction

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        X = []
        cols = state.vectorInfo()
        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)

            for action in actions:
                newState, outcome = GM.activate(board, state, action)
                X.append(np.array(newState.vector()))
        df = pd.DataFrame(data=X, columns=cols)
        score = self.model.predict_proba(df)
        scores = list(zip(score, actions))
        bestaction = self.bestAction(scores)
        if not bestaction:
            raise ValueError('No action given')
        # print("SCHOOSEACTION", bestaction)
        return bestaction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        X = []
        cols = state.vectorInfo()
        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassResponse(self.team)] + \
                      GM.buildResponses(board, state, figure)

            for action in actions:
                newState, outcome = GM.activate(board, state, action)
                X.append(np.array(newState.vector()))
        df = pd.DataFrame(data=X, columns=cols)
        score = self.model.predict_proba(df)
        scores = list(zip(score, actions))
        bestaction = self.bestAction(scores)
        if not bestaction:
            raise ValueError('No action given')
        # print("SCHOOSEACTION", bestaction)
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
