

from agents import GreedyAgent
from agents.ml.classifier import ClassifierAgent
from agents.matchmanager import MatchManager
from core.const import RED, BLUE
from agents.ml.regressionMulti import RegressionMultiAgent
from utils.setup_logging import setup_logging
from scenarios import scenarioJunction
import logging


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()

    '''seed = 50
    red_models = [
        ('models\\Junction_RandomForestRegressor_red_attack_20210221.joblib'),
        ('models\\Junction_RandomForestRegressor_red_move_20210221.joblib'),
        ('models\\Junction_RandomForestRegressor_red_pass_20210221.joblib'),

    ]
    blue_models = [
        ('models\\Junction_RandomForestRegressor_blue_attack_20210221.joblib'),
        ('models\\Junction_RandomForestRegressor_blue_move_20210221.joblib'),
        ('models\\Junction_RandomForestRegressor_blue_pass_20210221.joblib'),

    ]

    board, state = scenarioJunction()


    playerRed = RegressionMultiAgent(RED, red_models[0], red_models[1], red_models[2], seed)
    playerBlue = RegressionMultiAgent(BLUE, blue_models[0], blue_models[1], blue_models[2], seed)

    mm = MatchManager(' ', playerRed, playerBlue, board, state, seed=seed)

    while not mm.end:
        mm.nextStep()

    print('winner: ', mm.winner)


    '''
    seed = 151775519

    board, state = scenarioJunction()
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

    red = ClassifierAgent(RED, red_models[1][1], seed=seed)
    blue = ClassifierAgent(BLUE, blue_models[1][1], seed=seed)

    # red = RegressionAgent(RED, 'models/Junction_RandomForestRegressor_red_20210215.joblib', seed=seed)
    # blue = RegressionAgent(BLUE, 'models/Junction_RandomForestRegressor_blue_20210215.joblib', seed=seed)

    #red = GreedyAgent(RED, seed=seed)
    #blue = GreedyAgent(BLUE, seed=seed)

    mm = MatchManager(' ', red, blue, board, state, seed=seed)
    while not mm.end:
        mm.nextStep()
    print('winner: ', mm.winner)


