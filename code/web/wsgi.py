import logging.config
import os.path as op
import yaml

from web.server import create_app as game_app

dir_path = op.dirname(op.realpath(__file__))

with open(op.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

application = game_app()

if __name__ == '__main__':
    pass
