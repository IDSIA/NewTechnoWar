import time
import numpy as np
import unittest

from agents import buildMatchManager


class TestAttackAction(unittest.TestCase):

    def _testJunction100(self):
        seed = 42
        np.random.seed(seed)

        timings = []

        for _ in range(100):

            seed = np.random.randint(1, 1000000000)
            mm = buildMatchManager('', 'scenarioJunction', 'PlayerDummy', 'PlayerDummy', seed=seed)

            start = time.time()
            while not mm.end:
                mm.nextTurn()
            end = time.time()

            timings.append(end - start)

        print('Total execution time:  ', sum(timings))
        print('Average execution time:', sum(timings) / len(timings))
