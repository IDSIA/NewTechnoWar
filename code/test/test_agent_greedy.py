import unittest
from collections import Counter

from agents import GreedyAgent, MatchManager
from core.const import RED, BLUE
from scenarios import scenarioTest2v2, scenarioJunction


class TestAgentGreedy(unittest.TestCase):

    def setUp(self) -> None:
        self.red = GreedyAgent(RED)
        self.blue = GreedyAgent(BLUE)

    def test2v2(self):
        winners = []

        for i in range(1):
            board, state = scenarioTest2v2()
            mm = MatchManager('TestGreedyAgent2v2', self.red, self.blue, board, state, seed=i)

            while not mm.end:
                mm.step()

            winners.append(mm.winner)

        print(Counter(winners))

    def testJunction(self):
        winners = []

        for i in range(1):
            board, state = scenarioJunction()
            mm = MatchManager('TestGreedyAgentJunction', self.red, self.blue, board, state, seed=i)

            while not mm.end:
                mm.step()

            winners.append(mm.winner)

        print(Counter(winners))
