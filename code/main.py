import logging.config
import os.path as op

import yaml

from agents.matchmanager import MatchManager
from agents.ml.regressor import RegressorAgent
from core.const import RED, BLUE
from scenarios import scenarioJunction

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

if __name__ == '__main__':
    board, state = scenarioJunction()
    playerRed = RegressorAgent(RED, {'scenario': board.name, 'model': 'RandomForestRegressor', 'color': 'red'})
    playerBlue = RegressorAgent(BLUE, {'scenario': board.name, 'model': 'RandomForestRegressor', 'color': 'blue'})
    mm = MatchManager(' ', playerRed, playerBlue, board, state, seed=51)
    while not mm.end:
        mm.nextStep()

    print(
        len(mm.states_history),
        len(mm.actions_history)
    )
