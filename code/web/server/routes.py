import logging

from flask import Blueprint, render_template
from flask import current_app as app

from core.game import scenarios, GameManager
from web.server.utils import scroll

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main.route('/', methods=['GET'])
def index():
    """Serve list of available scenarios."""
    scenarios = [
        "scenarioTest1v1",
        "scenarioTest3v1",
        "scenarioTestBench"
    ]

    return render_template(
        'index.html',
        title='Home | NewTechnoWar',
        template='game-template',
        scenarios=scenarios
    )


@main.route('/game/<string:scenario>', methods=['GET'])
def game(scenario: str):
    """Serve game main page."""

    # TODO: theoretically, the key should be a UUID for the game
    gm: GameManager = getattr(scenarios, scenario)()
    app.games[scenario] = gm

    logging.info(f"Created game with scenario {gm.name}")

    return render_template(
        'game.html',
        title='Game | NewTechnoWar',
        template='game-template',
        board=list(scroll(gm.board))
    )
