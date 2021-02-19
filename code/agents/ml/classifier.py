from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.const import BLUE
from core.game import GameBoard, GameState, vectorState, vectorAction, vectorStateInfo, vectorActionInfo


class ClassifierAgent(MLAgent):

    def __init__(self, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__('ClassifierAgent', team, filename, randomChoice, seed)

    def scores(self, state: GameState, board: GameBoard, actions: List[Action]) -> List[Tuple[float, Action]]:
        X = [vectorState(state) + vectorAction(action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo()).dropna(axis=1)
        df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)

        idx = 1 if self.team == BLUE else 0
        scores = self.model.predict_proba(df)

        return [(scores[i][idx], actions[i]) for i in range(len(actions))]
