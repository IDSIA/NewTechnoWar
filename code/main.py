import logging.config
import os.path as op

import yaml

from agents.matchmanager import buildMatchManager

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

if __name__ == '__main__':
    mm = buildMatchManager('', 'scenarioTest2v2', 'GreedyAgent', 'GreedyAgent', seed=42)

    while not mm.end:
        mm.nextStep()
