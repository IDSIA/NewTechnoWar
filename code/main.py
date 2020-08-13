import logging.config
import os.path as op

import yaml

from agents.players import MatchManager

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

if __name__ == '__main__':
    mm = MatchManager('', 'scenarioTestBench', 'PlayerDummy', 'PlayerDummy', seed=24)

    while not mm.end:
        mm.nextTurn()
