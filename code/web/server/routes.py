import logging
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify, redirect
from flask import current_app as app

from agents.matchmanager import MatchManager, buildMatchManager
from web.server.utils import scroll, fieldShape

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")


@main.route("/", methods=["GET", "POST"])
def index():
    """Serve list of available scenarios."""
    if request.method == 'POST':
        data = request.form

        mm = buildMatchManager(
            str(uuid.uuid4()),
            data['scenario'],
            data['redPlayer'],
            data['bluePlayer'],
        )
        app.games[mm.gid] = mm
        mm.step()

        logging.info(f"Created game #{mm.gid} with scenario {mm.board.name}")

        response = make_response(
            redirect(f'/game/')
        )
        response.set_cookie("gameId", mm.gid)

    else:
        logging.info(f"New lobby access")

        scenarios = [
            'scenarioTest1v1',
            'scenarioTest2v2',
            'scenarioTest3v1',
            'scenarioTestBench',
            'scenarioDummy1',
            'scenarioDummy2',
            'scenarioDummy3',
            'scenarioDummyResponseCheck',
            'scenarioInSightTest',
            'scenarioJunction',
        ]

        players = [
            # "Human", TODO
            "PlayerDummy",
        ]

        response = make_response(
            render_template(
                "index.html",
                title="Home | NewTechnoWar",
                template="game-template",
                scenarios=scenarios,
                players=players
            )
        )
        response.delete_cookie("gameId")

    return response


def checkGameId() -> (str, MatchManager):
    if "gameId" not in request.cookies:
        raise ValueError('GameId is missing!')

    gameId = request.cookies["gameId"]

    if gameId not in app.games:
        raise ValueError("GameId not registered")

    mm: MatchManager = app.games[gameId]

    return gameId, mm


@main.route("/game/", methods=["GET"])
def game():
    """Serve game main page."""

    try:
        gameId, mm = checkGameId()

        logging.info(f"Restored game #{gameId} with scenario {mm.board.name}")

        response = make_response(
            render_template(
                "game.html",
                title="Game | NewTechnoWar",
                template="game-template",
                board=list(scroll(mm.board)),
                gameId=gameId,
                shape=fieldShape(mm.board),
                turn=mm.state.turn
            )
        )

        response.set_cookie("gameId", gameId)
        return response

    except ValueError as ve:
        logging.error(ve)
        return redirect('/')


@main.route("/game/reset", methods=['GET'])
def gameReset():
    try:
        _, mm = checkGameId()
        mm.reset()

        response = make_response(
            redirect(f'/game/')
        )

        response.delete_cookie("gameId")
        return response

    except ValueError as ve:
        logging.error(ve)
        return redirect('/')


@main.route("/game/state", methods=["GET"])
def gameState():
    logging.info("Request state")

    try:
        _, mm = checkGameId()
        return jsonify({
            'state': mm.state
        }), 200

    except ValueError as e:
        logging.error(e)
        return None, 404


@main.route("/game/next/step", methods=["GET"])
def gameNextStep():
    logging.info("Request next")

    try:
        _, mm = checkGameId()
        mm.nextStep()

        lastAction = None
        lastOutcome = None

        if not mm.update:
            lastAction = mm.actionsDone[-1]
            lastOutcome = mm.outcome[-1]

        return jsonify({
            'update': mm.update,
            'end': mm.end,
            'state': mm.state,
            'action': lastAction,
            'outcome': lastOutcome,
        }), 200

    except ValueError as e:
        logging.error(e)
        return None, 404


@main.route("/game/next/turn", methods=["GET"])
def gameNextTurn():
    logging.info("Request next")

    try:
        _, mm = checkGameId()
        mm.nextTurn()

        lastAction = mm.actionsDone[-1]

        return jsonify({
            'update': mm.update,
            'end': mm.end,
            'state': mm.state,
            'action': lastAction,
        }), 200

    except ValueError as e:
        logging.error(e)
        return None, 404
