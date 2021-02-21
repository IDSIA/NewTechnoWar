from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState, vectorState, vectorStateInfo, vectorAction, vectorActionInfo


class RegressionMultiAgent(MLAgent):

    #ragionare in modo da divere i data azioni dai movimenti e pass

    def __init__(self, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__('RegressorMultiAgent', team, filename, randomChoice, seed)

    def scores(self, state: GameState, board: GameBoard, actions: List[Action]) -> List[Tuple[float, Action]]:
        X = [vectorState(state) + vectorAction(action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo()).dropna(axis=1)
        df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)

        #qui vorrei fare un controllo su quale modello utilizzare
        scores = self.model.predict(df)

        return list(zip(scores, actions))
