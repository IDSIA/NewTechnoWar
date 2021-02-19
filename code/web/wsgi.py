from utils.setup_logging import setup_logging
from web.server import create_app as game_app

setup_logging()

application = game_app()

if __name__ == '__main__':
    pass
