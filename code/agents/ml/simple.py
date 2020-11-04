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
        self.model = params['model'] #quando creo l'agente gli passo il modello
        #DOMANDA, problema che io ho un modello per ogni scenario, come si gestisce questa cosa?

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
                #score è un numpy array, dove 0 è per il blu mentre 1 è per il rosso

                scores.append((score, action))
                #in scores avrò tutte le probabilità legata a quella specifica azione

        # find better action
        bestScore, bestAction = 0.0, None

        for score, action in scores:
            if score > bestScore:
                bestScore, bestAction = score, action
        #sarà qui che devo già selezionare lo score del giocatore, se si tratta del blue o del rosso


        #devo usare team? stile if self.team== red allora else altro?
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
