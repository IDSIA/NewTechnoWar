import unittest

from core.const import RED, BLUE
from core.templates import collect
from scenarios import buildScenario


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        collect()

    def testScenarioJunction(self):
        board, state = buildScenario('Junction')

        redsIdx = [x.index for x in state.figures[RED]]
        bluesIdx = [x.index for x in state.figures[BLUE]]

        self.assertEqual(len(redsIdx), len(set(redsIdx)), "reds have duplicated index!")
        self.assertEqual(len(bluesIdx), len(set(bluesIdx)), "reds have duplicated index!")
