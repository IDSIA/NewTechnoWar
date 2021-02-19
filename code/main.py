import logging.config
import os.path as op

import pandas as pd
import yaml

from agents import GreedyAgent
from agents.matchmanager import MatchManager
from core.const import RED, BLUE
from core.vectors import vectorActionInfo, vectorAction, vectorStateInfo, vectorState
from scenarios import scenarioJunction

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

if __name__ == '__main__':
    seed = 151775519

    board, state = scenarioJunction()

    # red = ClassifierAgent(RED, 'models/Junction_RandomForestClassifier_red_20210215.joblib', seed=seed)
    # blue = ClassifierAgent(BLUE, 'models/Junction_RandomForestClassifier_blue_20210215.joblib', seed=seed)

    # red = RegressionAgent(RED, 'models/Junction_RandomForestRegressor_red_20210215.joblib', seed=seed)
    # blue = RegressionAgent(BLUE, 'models/Junction_RandomForestRegressor_blue_20210215.joblib', seed=seed)

    # red = GreedyAgent(RED, seed=seed)
    # blue = GreedyAgent(BLUE, seed=seed)

    # scenarioJunction RandomAgent GreedyAgent 151775519
    red = GreedyAgent(RED)
    blue = GreedyAgent(BLUE)

    mm = MatchManager(' ', red, blue, board, state, seed=seed)
    while not mm.end:
        mm.nextStep()

    actions_cols = vectorActionInfo()
    actions_data = [vectorAction(x) for x in mm.actions_history]

    df_actions = pd.DataFrame(columns=actions_cols, data=actions_data)

    states_cols = vectorStateInfo()
    states_data = [vectorState(x) for x in mm.states_history]

    df_states = pd.DataFrame(columns=states_cols, data=states_data)

    df_red = mm.red.createDataFrame()
    df_blue = mm.blue.createDataFrame()
