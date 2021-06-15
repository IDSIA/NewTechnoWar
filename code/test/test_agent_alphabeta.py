import unittest

from os.path import join, dirname

from agents import MatchManager, AlphaBetaAgent, RandomAgent
from core.const import BLUE, RED
from core.scenarios import buildScenario
from utils.setup_logging import setup_logging

setup_logging(join(dirname(__file__), 'logger.config.yaml'))


class TestAgentAlphaBeta(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

    @unittest.skip('Used only for debug')
    def testAgainstRandom(self):
        r = AlphaBetaAgent(RED, maxDepth=7, timeLimit=5)
        b = RandomAgent(BLUE)
        board, state = buildScenario('Junction')

        mm = MatchManager('', r, b, board, state, 24)

        while not mm.end:
            mm.nextStep()
