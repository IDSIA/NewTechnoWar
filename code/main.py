import logging

import numpy

from agents.adversarial.alphabetafast1 import AlphaBetaFast1Agent
from agents.matchmanager import MatchManager
from core.const import RED, BLUE
from scenarios import buildScenario
from utils.setup_logging import setup_logging

numpy.seterr('raise')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()

    seed = 151775519
    board, state = buildScenario('Junction')

    """
    red_models = [
        ('models\\Junction_RandomForestRegressor_red_attack_20210227.joblib'),
        ('models\\Junction_RandomForestRegressor_red_move_20210227.joblib'),
        ('models\\Junction_RandomForestRegressor_red_pass_20210227.joblib'),

    ]
    blue_models = [
        ('models\\Junction_RandomForestRegressor_blue_attack_20210227.joblib'),
        ('models\\Junction_RandomForestRegressor_blue_move_20210227.joblib'),
        ('models\\Junction_RandomForestRegressor_blue_pass_20210227.joblib'),
    ]
    
    red = RegressionMultiAgent(RED, red_models[0], red_models[1], red_models[2], seed)
    blue = RegressionMultiAgent(BLUE, blue_models[0], blue_models[1], blue_models[2], seed)
    """

    """
    red_models = [
        ('gre', ''),
        ('cls', 'models\\Junction_RandomForestClassifier_red.joblib'),
        ('cls', 'models\\Junction_RandomForestClassifier.joblib'),
        ('reg', 'models\\Junction_RandomForestRegressor_red.joblib'),
        ('reg', 'models\\Junction_RandomForestRegressor.joblib'),
    ]
    
    blue_models = [
        ('gre', ''),
        ('cls', 'modelS\\Junction_RandomForestClassifier_blue.joblib'),
        ('cls', 'models\\Junction_RandomForestClassifier.joblib'),
        ('reg', 'models\\Junction_RandomForestRegressor_blue.joblib'),
        ('reg', 'models\\Junction_RandomForestRegressor.joblib'),
    ]
    """

    # red = ClassifierAgent(RED, red_models[1][1], seed=seed)
    # blue = ClassifierAgent(BLUE, blue_models[1][1], seed=seed)

    # red = RegressionAgent(RED, 'models/Junction_RandomForestRegressor_red_20210215.joblib', seed=seed)
    # blue = RegressionAgent(BLUE, 'models/Junction_RandomForestRegressor_blue_20210215.joblib', seed=seed)

    # red = GreedyAgent(RED, seed=seed)
    # blue = GreedyAgent(BLUE, seed=seed)

    red = AlphaBetaFast1Agent(RED, maxDepth=3)
    blue = AlphaBetaFast1Agent(BLUE, maxDepth=3)

    mm = MatchManager(' ', red, blue, board, state, seed=seed)
    while not mm.end:
        mm.nextStep()

    logger.info('winner: ', mm.winner)

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
