import os

import joblib

from typing import List, Tuple

import pandas as pd

from agents.ml.simple import MLAgent
from core.actions import Action
from core.game import GameBoard, GameState, vectorState, vectorStateInfo
from core.vectors import vectorAction, vectorActionInfo, vectorBoard, vectorBoardInfo


class RegressionMultiAgent(MLAgent):

    # ragionare in modo da divere i data azioni dai movimenti e pass

    def __init__(self, team: str, filename_a: str, filename_m: str, filename_p: str, seed=0, randomChoice=False):
        super().__init__('RegressorMultiAgent', team, filename_a, randomChoice, seed)
        self.model_a = joblib.load(os.path.join(os.getcwd(), filename_a))
        self.model_m = joblib.load(os.path.join(os.getcwd(), filename_m))
        self.model_p = joblib.load(os.path.join(os.getcwd(), filename_p))

    def scores(self, state: GameState, board: GameBoard, actions: List[Action]) -> List[Tuple[float, Action]]:
        #actions = [a for a in actions if a.__class__.__name__ is not "PassFigure"]
        X = [vectorState(state) + vectorAction(action) + vectorBoard(board, state, action) for action in actions]

        df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo() + vectorBoardInfo()).dropna(axis=1)

        df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)
        df['action_obj'] = actions

        df_m = df.loc[((df['action_type_Move']) | (df['action_type_MoveLoadInto']))].copy()
        df_m_obj = df_m['action_obj']
        df_m.drop('action_obj', 1, inplace=True)

        df_a = df.loc[
            ((df['action_type_Attack']) | (df['action_type_AttackGround']) | (
                df['action_type_AttackRespond']))].copy()
        df_a_obj = df_a['action_obj']
        df_a.drop('action_obj', 1, inplace=True)

        df_p = df.loc[((df['action_type_Pass']) | (df['action_type_PassFigure']) | (
            df['action_type_PassTeam']) | (df['action_type_PassRespond']))].copy()
        df_p_obj = df_p['action_obj']
        df_p.drop('action_obj', 1, inplace=True)

        score_m = []
        if not df_m.empty:
            y_m = self.model_m.predict(df_m)
            score_m = list(zip(y_m, df_m_obj))
        score_p = []
        if not df_p.empty:
            y_p = self.model_p.predict(df_m)
            score_p = list(zip(y_p, df_p_obj))
        score_a = []
        if not df_a.empty:
            y_a = self.model_a.predict(df_a)
            score_a = list(zip(y_a, df_a_obj))
        return score_a + score_m + score_p

