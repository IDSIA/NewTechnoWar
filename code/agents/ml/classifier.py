from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.const import BLUE
from core.game import GameBoard, GameState, vectorState, vectorStateInfo
from core.vectors import vectorAction, vectorActionInfo, vectorBoard, vectorBoardInfo

# NOTE: deprecated, see agents.ml.__init__.py file


class ClassifierAgent(MLAgent):
    """
    BAsed on Classification models.
    """

    def __init__(self, team: str, filename: str, randomChoice=False, tops: int = 10, seed=0):
        """
        :param team:            color of the team
        :param filename:        path to the model file stored on disk
        :param randomChoice:    if true, in case of same score the action is chosen randomly
        :param tops:            if randomChoice is true, this defines the pool of top N actions to chose from
        :param seed:            random seed to use internally
        """
        super().__init__('ClassifierAgent', team, filename, randomChoice, tops, seed)

    def scores(self, board: GameBoard, state: GameState, actions: List[Action]) -> List[Tuple[float, Action]]:
        """
        :param board:       board of the game
        :param state:       state of the game
        :param actions:     list of available actions to score
        :return: list of all actions with their score
        """
        X = [vectorState(state) + vectorAction(action) + vectorBoard(board, state, action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo() + vectorBoardInfo()).dropna(axis=1)
        df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)

        offset = 1 if self.team == BLUE else 0
        scores = self.model.predict_proba(df)

        return [(abs(offset - scores[i][0]), actions[i]) for i in range(len(actions))]
