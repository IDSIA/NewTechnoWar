import logging
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify
from flask import current_app as app

from core.game import scenarios, GameManager
from web.server.utils import scroll, fieldShape

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")


@main.route("/", methods=["GET"])
def index():
    """Serve list of available scenarios."""
    scenarios = [
        "scenarioTest1v1",
        "scenarioTest3v1",
        "scenarioTestBench"
    ]

    return render_template(
        "index.html",
        title="Home | NewTechnoWar",
        template="game-template",
        scenarios=scenarios
    )


@main.route("/game/<string:scenario>", methods=["GET"])
def game(scenario: str):
    """Serve game main page."""

    if "gameId" in request.cookies:
        gameId = request.cookies["gameId"]
    else:
        gameId = str(uuid.uuid4())

    if gameId in app.games:
        gm: GameManager = app.games[gameId]
    else:
        gm: GameManager = getattr(scenarios, scenario)()
        app.games[gameId] = gm

    logging.info(f"Created game #{gameId} with scenario {gm.name}")

    response = make_response(
        render_template(
            "game.html",
            title="Game | NewTechnoWar",
            template="game-template",
            board=list(scroll(gm.board)),
            gameId=gameId,
            shape=fieldShape(gm.board)
        )
    )

    response.set_cookie("gameId", gameId)
    return response


@main.route("/game/figures", methods=["GET"])
def gameFigures():
    logging.info("Request figures")

    if "gameId" not in request.cookies:
        logging.error("Game id missing")
        return None, 404

    gameId = request.cookies["gameId"]
    gm: GameManager = app.games[gameId]

    return jsonify(gm.figures), 200
