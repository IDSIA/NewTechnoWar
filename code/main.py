import logging.config
import os.path as op

import yaml

from agents.matchmanager import buildMatchManager

from agents.matchmanager import MatchManager

from itertools import product

from agents import GreedyAgent, AlphaBetaAgent, RandomAgent
from agents.ml.regressor import RegressorAgent
from scenarios import scenarioJunction, scenarioJunctionExo, scenarioTest1v1, scenarioTest2v2
from core.const import RED, BLUE
from agents.ml.simple import SimpleMLAgent
import json

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

if __name__ == '__main__':
    board, state = scenarioJunction()
    playerRed = RandomAgent(RED)#, {'scenario': board.name, 'model': 'RandomForestRegressor', 'color': 'red'})
    playerBlue = RegressorAgent(BLUE, {'scenario': board.name, 'model': 'RandomForestRegressor', 'color': 'blue'})
    mm = MatchManager(' ', playerRed, playerBlue, board, state, seed=42)
    while not mm.end:
        mm.nextStep()
