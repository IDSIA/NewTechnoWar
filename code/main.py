import logging

import pandas as pd

from agents import RegressionMultiAgent, ClassifierAgent, RegressionAgent, GreedyAgent
from agents.adversarial.alphabetafast1 import AlphaBetaFast1Agent
from agents.matchmanager import MatchManager
from core.const import RED, BLUE
from core.game import vectorStateInfo, vectorState
from core.scenarios import buildScenario
from core.vectors import vectorActionInfo, vectorAction, vectorBoardInfo, vectorBoard
from utils.setup_logging import setup_logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()

    # random seed for repeatability
    seed = 151775519

    # the available maps depend on the current config files
    board, state = buildScenario('Junction')

    ''' 
    # to use Agents based on ML, it is mandatory to load the required models
    red = RegressionMultiAgent(RED,
                               'models/Junction_red_attack.joblib',
                               'models/Junction_red_move.joblib',
                               'models/Junction_red_pass.joblib',
                               seed)
    blue = RegressionMultiAgent(BLUE,
                                'models/Junction_blue_attack.joblib',
                                'models/Junction_blue_move.joblib',
                                'models/Junction_blue_pass.joblib',
                                seed)

    # agents that use classifiers or regressors just need one model
    red = ClassifierAgent(RED, 'models/Junction_cls_red.joblib', seed=seed)
    blue = ClassifierAgent(BLUE, 'models/Junction_cls_blue.joblib', seed=seed)

    red = RegressionAgent(RED, 'models/Junction_reg_red.joblib', seed=seed)
    blue = RegressionAgent(BLUE, 'models/Junction_reg_blue.joblib', seed=seed)
    '''

    # greedy agents instead don't require models
    red = GreedyAgent(RED, seed=seed)
    blue = GreedyAgent(BLUE, seed=seed)
    '''

    # different agents can have different set of parameters
    red = AlphaBetaFast1Agent(RED, maxDepth=3)
    blue = AlphaBetaFast1Agent(BLUE, maxDepth=3)
    '''

    # the MatchManager is the object that is in charge of control the evolution of a game
    mm = MatchManager('', red, blue, board, state, seed=seed)

    # there is a dedicated method to play the full game
    mm.play()

    # at the end it is possible to collect some information from the MatchManager object, like the winner
    logger.info('winner: ', mm.winner)

    # it is also possible to get information on the history of played actions...
    actions_cols = vectorActionInfo()
    actions_data = [vectorAction(x) for x in mm.actions_history]

    df_actions = pd.DataFrame(columns=actions_cols, data=actions_data)

    # ...on the states...
    states_cols = vectorStateInfo()
    states_data = [vectorState(x) for x in mm.states_history]

    df_states = pd.DataFrame(columns=states_cols, data=states_data)

    # ...on the board...
    board_cols = vectorBoardInfo()
    board_data = [vectorBoard(board, s, a) for s, a in zip(mm.states_history, mm.actions_history)]

    df_board = pd.DataFrame(columns=board_cols, data=board_data)

    print(df_states.shape, df_actions.shape, df_board.shape)

    # ...or collect a DataFrame on everything
    df_red = mm.red.createDataFrame()
    df_blue = mm.blue.createDataFrame()

    # btw, this main is just an example: it will not work until you comment out the the agents with the models...
    # ...or you build the missing models ;)
