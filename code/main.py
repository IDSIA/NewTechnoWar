import logging.config
import os.path as op

import numpy
import yaml

from agents.adversarial.alphabetafast1 import AlphaBetaFast1Agent
from agents.matchmanager import MatchManager
from core.const import RED, BLUE
from scenarios import scenarioJunction

numpy.seterr('raise')

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
    red = AlphaBetaFast1Agent(RED, maxDepth=12)
    blue = AlphaBetaFast1Agent(BLUE, maxDepth=3)

    mm = MatchManager(' ', red, blue, board, state, seed=seed)
    while not mm.end:
        mm.nextStep()

    # actions_cols = vectorActionInfo()
    # actions_data = [vectorAction(x) for x in mm.actions_history]

    # df_actions = pd.DataFrame(columns=actions_cols, data=actions_data)

    # states_cols = vectorStateInfo()
    # states_data = [vectorState(x) for x in mm.states_history]

    # df_states = pd.DataFrame(columns=states_cols, data=states_data)

    # board_cols = vectorBoardInfo()
    # board_data = [vectorBoard(board, s, a) for s, a in zip(mm.states_history, mm.actions_history)]

    # df_board = pd.DataFrame(columns=board_cols, data=board_data)

    # print(df_states.shape, df_actions.shape, df_board.shape)

    # df_red = mm.red.createDataFrame()
    # df_blue = mm.blue.createDataFrame()
