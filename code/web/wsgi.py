from werkzeug.middleware.dispatcher import DispatcherMiddleware

from web.server import create_app as game_app

application = DispatcherMiddleware(game_app(), {})

if __name__ == '__main__':
    pass
