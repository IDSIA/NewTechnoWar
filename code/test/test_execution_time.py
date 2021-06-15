import time
import unittest

import numpy as np
from os.path import join, dirname

from agents import buildMatchManager
from utils.setup_logging import setup_logging

setup_logging(join(dirname(__file__), 'logger.config.yaml'))


class TestAttackAction(unittest.TestCase):

    @unittest.skip('Used only for profiling')
    def testJunction100(self):
        seed = 42
        np.random.seed(seed)

        timings = []

        for _ in range(100):

            seed = np.random.randint(1, 1000000000)
            mm = buildMatchManager('', 'Junction', 'PlayerDummy', 'PlayerDummy', seed=seed)

            start = time.time()
            while not mm.end:
                mm.nextTurn()
            end = time.time()

            timings.append(end - start)

        print('Total execution time:  ', sum(timings))
        print('Average execution time:', sum(timings) / len(timings))
