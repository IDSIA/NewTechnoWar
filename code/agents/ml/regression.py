from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.game import GameBoard, GameState, vectorState, vectorStateInfo
from core.vectors import vectorAction, vectorActionInfo, vectorBoard, vectorBoardInfo


class RegressionAgent(MLAgent):

    def __init__(self, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__('RegressorAgent', team, filename, randomChoice, seed)

    def scores(self, state: GameState, board: GameBoard, actions: List[Action]) -> List[Tuple[float, Action]]:
        X = [vectorState(state) + vectorAction(action) + vectorBoard(board, state, action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo() + vectorBoardInfo()).dropna(axis=1)
        df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)

        scores = self.model.predict(df)

        return list(zip(scores, actions))
