from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.game.state import GameState, vectorState, vectorStateInfo


class RegressionAgent(MLAgent):

    def __init__(self, team: str, filename: str, randomChoice=False, seed=0):
        super().__init__('RegressorAgent', team, filename, randomChoice, seed)

    def scores(self, state: GameState, actions: List[Action]) -> List[Tuple[float, Action]]:
        X = [vectorState(state, action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo()).dropna(axis=1)
        df = df[[c for c in df.columns if self.team in c]]  # TODO: move this to the pipeline

        scores = self.model.predict(df)

        return list(zip(scores, actions))
