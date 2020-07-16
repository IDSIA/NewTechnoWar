import logging
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify, redirect
from flask import current_app as app

from core import BLUE, RED
from web.server.players.__init__ import PlayerDummy, MatchManager
from web.server.utils import scroll, fieldShape

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")


@main.route("/", methods=["GET"])
def index():
    """Serve list of available scenarios."""
    scenarios = [
        "scenarioTest1v1",
        "scenarioTest2v2",
        "scenarioTest3v1",
        "scenarioTestBench"
    ]

    response = make_response(
        render_template(
            "index.html",
            title="Home | NewTechnoWar",
            template="game-template",
            scenarios=scenarios
        )
    )

    response.delete_cookie("gameId")
    return response


@main.route("/game/<string:scenario>", methods=["GET"])
def game(scenario: str):
    """Serve game main page."""

    if "gameId" in request.cookies:
        gameId = request.cookies["gameId"]
    else:
        gameId = str(uuid.uuid4())

    if gameId in app.games:
        mm: MatchManager = app.games[gameId]

        logging.info(f"Restored game #{gameId} with scenario {mm.gm.name}")
    else:
        mm = MatchManager(
            scenario,
            # TODO: let these two be configurable
            PlayerDummy(RED),
            PlayerDummy(BLUE)
        )
        app.games[gameId] = mm

        logging.info(f"Created game #{gameId} with scenario {mm.gm.name}")

    response = make_response(
        render_template(
            "game.html",
            title="Game | NewTechnoWar",
            template="game-template",
            board=list(scroll(mm.gm.board)),
            gameId=gameId,
            shape=fieldShape(mm.gm.board),
            turn=mm.turn
        )
    )

    response.set_cookie("gameId", gameId)
    return response


@main.route("/game/reset", methods=['GET'])
def gameReset():
    if "gameId" not in request.cookies:
        logging.error("Game id missing")
        return redirect('/')

    gameId = request.cookies["gameId"]

    if gameId not in app.games:
        logging.error("Game id not registered")
        return redirect('/')

    mm: MatchManager = app.games[gameId]

    response = make_response(
        redirect(f'/game/{mm.scenario}')
    )

    response.delete_cookie("gameId")
    return response


@main.route("/game/figures", methods=["GET"])
def gameFigures():
    logging.info("Request figures")

    if "gameId" not in request.cookies:
        logging.error("Game id missing")
        return None, 404

    mm: MatchManager = app.games[request.cookies["gameId"]]

    return jsonify(mm.gm.state.figures), 200


@main.route("/game/next/step", methods=["GET"])
def gameNextStep():
    logging.info("Request next")

    if "gameId" not in request.cookies:
        logging.error("Game id missing")
        return None, 404

    mm: MatchManager = app.games[request.cookies["gameId"]]

    mm.nextStep()

    lastAction = None
    lastOutcome = None
    if not mm.update:
        lastAction = mm.actionsDone[-1]
        lastOutcome = mm.outcome[-1]

    return jsonify({
        'turn': mm.turn,
        'update': mm.update,
        'action': lastAction,
        'outcome': lastOutcome,
    }), 200


@main.route("/game/next/turn", methods=["GET"])
def gameNextTurn():
    logging.info("Request next")

    if "gameId" not in request.cookies:
        logging.error("Game id missing")
        return None, 404

    mm: MatchManager = app.games[request.cookies["gameId"]]

    n = len(mm.actionsDone) - 1
    mm.nextTurn()
    lastAction = mm.actionsDone[n:]

    return jsonify({'turn': mm.turn, 'update': mm.update, 'actions': lastAction}), 200
