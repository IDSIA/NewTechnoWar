from utils.setup_logging import setup_logging

setup_logging()

from web.backend import create_app as game_app

application = game_app()

if __name__ == '__main__':
    pass
