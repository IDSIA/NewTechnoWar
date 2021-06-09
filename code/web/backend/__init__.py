"""Initialize application"""
import logging

from flask import Flask

from core.templates import collect, TMPL_SCENARIOS, TMPL_TERRAIN_TYPE
from web.backend.config import conf
from web.backend.utils.serializer import GameJSONEncoder

logger = logging.getLogger(__name__)


def create_app():
    """Construct the core application."""
    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder="templates",
        static_folder="static"
    )

    # Application Configuration
    app.config.from_object(conf)
    app.json_encoder = GameJSONEncoder

    # list of all available agents
    app.players = [
        'Human',  # this should be "interactive"
        'RandomAgent',
        'GreedyAgent',
        'AlphaBetaAgent',
        'AlphaBetaFast1Agent',
    ]

    # parameters for games
    app.games = dict()
    app.params = dict()
    app.actions = dict()
    app.terrains = dict()
    app.scenarios = list()

    # this is for the control of data collection
    app.collecting = False

    def collect_config():
        if app.collecting:
            return

        app.collecting = True
        try:
            collect()
            app.scenarios = [k for k, v in TMPL_SCENARIOS.items() if 'offline' not in v]
            app.terrains = {v['level']: v for k, v in TMPL_TERRAIN_TYPE.items()}
        except Exception as e:
            logger.error(f'could not collect configuration! {e}')
        finally:
            app.collecting = False

    app.collect_config = collect_config

    with app.app_context():
        # Import parts of our application
        from . import routes
        app.register_blueprint(routes.main)

        return app
