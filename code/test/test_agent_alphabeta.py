import logging.config
import os.path as op
import unittest

import yaml

from agents import MatchManager, AlphaBetaAgent, RandomAgent
from core.const import BLUE, RED
from scenarios import scenarioJunction

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)


class TestAgentAlphaBeta(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

    @unittest.skip('Used only for debug')
    def testAgainstRandom(self):
        r = AlphaBetaAgent(RED, maxDepth=7, timeLimit=5)
        b = RandomAgent(BLUE)
        board, state = scenarioJunction()

        mm = MatchManager('', r, b, board, state, 24)

        while not mm.end:
            mm.nextStep()
