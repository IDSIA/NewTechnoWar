from agents import Agent
from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState
from agents import Agent, MatchManager, GreedyAgent
import numpy as np
import pandas as pd


class SimpleMLAgent(Agent):

    def __init__(self, team: str, params: dict):
        super().__init__('SimpleML', team)

        self.params: dict = params
        self.model = params['model']  # has .predict(X) -> np.array

    def encoder(self, X) -> tuple:
        return X

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)

            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                # apply classification pipeline
                X = newState.vector()
                score = self.model.predict_proba(X)

                scores.append((score, action))

        # find better action
        bestScore, bestAction = 0.0, None

        for score, action in scores:
            if score > bestScore:
                bestScore, bestAction = score, action

        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        # TODO: get inspiration from GreedyAgent.chooseResponse()
        '''scores = [self.scorePass(board, state)]

        # compute all scores for possible responses
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scoreResponse(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)
        #logging.info(f'{self.team:5}: {action} ({score})')''

        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea?
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        # TODO: find a better idea? now random
        colors = list(state.choices[self.team].keys())
        color = np.random.choice(colors)

        state.choose(self.team, color)'''
