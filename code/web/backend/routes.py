import logging
import os
import random
from typing import Tuple
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify, redirect, send_file
from flask import current_app as app
from flask_cors import CORS

from agents import Agent, Human, MatchManager, buildMatchManager
from core.const import BLUE, RED
from core.templates import *
from web.backend.images import board2png, scenario2png

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')
cors = CORS(main, resources={r'/api/*': {'origins': '*'}})


@main.route('/', methods=['GET', 'POST'])
# TODO: change this to serve the new webapp
def index():
    """Serve list of available scenarios."""
    if request.method == 'POST':
        try:
            if app.config['DEBUG']:
                logger.info('Using debug configuration!')
                redPlayer = 'GreedyAgent'
                bluePlayer = 'GreedyAgent'
                scen = 'Junction'
                autoplay = True
                seed = 0
                replay = ''
            else:
                data = request.form
                seed = int(data['seed'])

                redPlayer = data['redPlayer']
                bluePlayer = data['bluePlayer']

                autoplay = 'autoplay' in data or redPlayer == 'Human' or bluePlayer == 'Human'
                scen = data['scenario']
                replay = data['replay']

            mm = buildMatchManager(
                str(uuid.uuid4()),
                scen,
                redPlayer,
                bluePlayer,
                seed if seed > 0 else random.randint(1, 1000000000)
            )
            # mm.step() TODO: no more init until humans have chosen the start positions

            app.games[mm.gid] = mm
            app.params[mm.gid] = {
                'seed': mm.seed,
                'scenario': scen,
                'player': {RED: redPlayer, BLUE: bluePlayer},
                'autoplay': autoplay,
                'replay': replay,
            }
            app.actions[mm.gid] = None

            logger.info(f'Created game #{mm.gid} with scenario {mm.board.name}')

            response = make_response(
                redirect(f'/game/')
            )
            response.set_cookie('gameId', mm.gid)
        except Exception as e:
            logger.exception(e)
            return redirect('/')
    else:
        logger.info(f'New lobby access')

        app.collect_config()

        response = make_response(
            render_template(
                'index.html',
                title='Home | NewTechnoWar',
                template='game-template',
                scenarios=app.scenarios,
                players=app.players,
            )
        )
        response.delete_cookie('gameId')

    return response


@main.route('/api/config/template/<name>', methods=['GET'])
def configTemplate(name: str):
    data = None

    if name == 'weapons':
        data = TMPL_WEAPONS
    if name == 'figures':
        data = TMPL_FIGURES
    if name == 'status':
        data = TMPL_FIGURES_STATUS_TYPE
    if name == 'terrain':
        data = TMPL_TERRAIN_TYPE
    if name == 'boards':
        data = TMPL_BOARDS
    if name == 'scenarios':
        data = TMPL_SCENARIOS

    if data:
        return jsonify(data), 200

    return jsonify({'error': f'tamplate for {name} does not exits'}), 404


@main.route('/api/config/map/<name>', methods=['GET'])
def configMap(name: str):
    if '/' in name or '\\' in name or '.' in name:
        logger.warning(f'invalid map name! {name}')
        return ''

    logger.info(f'serving map for {name}')

    filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
    board2png(filename, name)

    response = send_file(filename, mimetype='image/png')
    response.headers.add('Cross-Origin-Resource-Policy', 'cross-origin')
    return response


@main.route('/api/config/scenario/<name>', methods=['GET'])
def configScenario(name: str):
    if '/' in name or '\\' in name or '.' in name:
        logger.warning(f'invalid map name! {name}')
        return ''

    logger.info(f'serving scenario for {name}')

    filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
    scenario2png(filename, name)

    response = send_file(filename, mimetype='image/png')
    response.headers.add('Cross-Origin-Resource-Policy', 'cross-origin')
    return response


def checkGameId() -> Tuple[str, MatchManager]:
    if 'gameId' not in request.cookies:
        raise ValueError('GameId is missing!')

    gameId = request.cookies['gameId']

    if gameId not in app.games:
        raise ValueError('GameId not registered')

    mm: MatchManager = app.games[gameId]

    return gameId, mm


@app.template_filter('autoversion')
def autoversion_filter(filename):
    try:
        path = os.path.join('gui/', filename[1:])
        timestamp = str(os.path.getmtime(path)).split('.')[0]
    except OSError:
        return filename

    return f'{filename}?v={timestamp}'


@main.route('/api/setup/data', methods=['GET'])
def getSetupData():
    app.collect_config()
    data = {
        'players': app.players,
        'scenarios': app.scenarios,
    }

    return jsonify(data), 200


@main.route('/api/game/start', methods=['POST'])
def postGameStart():
    data: dict = request.json
    errors: list = []
    ret_data: dict = {}

    logger.info(f'requested new game with data={data}')

    if app.config['DEBUG']:
        logger.info('Using debug configuration!')
        redPlayer = 'Human'
        bluePlayer = 'Human'
        scenario = 'TestBench'
        autoplay = False
        seed = 1
        ret_data['debug'] = True
    else:
        seed = int(data.get('seed', 0))

        redPlayer = ''
        bluePlayer = ''
        scenario = ''

        if 'red' in data and data['red'] in app.players:
            redPlayer = data['red']
        else:
            errors.append("Invalid or missing parameter for player 'red'")

        if 'blue' in data and data['blue'] in app.players:
            bluePlayer = data['blue']
        else:
            errors.append("Invalid or missing parameter for player 'blue'")

        if 'scenario' in data and data['scenario'] in app.scenarios:
            scenario = data['scenario']
        else:
            errors.append("Invalid or missing parameter for 'scenario'")

        autoplay = 'autoplay' in data or redPlayer == 'Human' or bluePlayer == 'Human'

    if errors:
        return jsonify({"error": errors}), 400

    mm = buildMatchManager(
        str(uuid.uuid4()),
        scenario,
        redPlayer,
        bluePlayer,
        seed if seed > 0 else random.randint(1, 1000000000)
    )

    app.games[mm.gid] = mm
    app.params[mm.gid] = {
        'seed': mm.seed,
        'scenario': scenario,
        'player': {RED: redPlayer, BLUE: bluePlayer},
        'autoplay': autoplay,
    }
    app.actions[mm.gid] = None
    ret_data['gameId'] = mm.gid
    ret_data['params'] = app.params[mm.gid]
    ret_data['terrains'] = app.terrains

    logger.info(f'Created game with gid={mm.gid} with scenario {mm.board.name}')

    return jsonify(ret_data), 200


@main.route('/api/game/reset/<gameId>', methods=['POST'])
def getGameReset(gameId: str):
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not valid.')

        mm: MatchManager = app.games[gameId]
        mm.reset()

        logger.info(f'Reset game #{gameId} with scenario {mm.board.name}')

        return jsonify({
            'gameId': gameId
        }), 200

    except ValueError as ve:
        logger.error(ve)
        return jsonify({
            'error': str(ve),
        }), 400


@main.route('/api/game/step/<gameId>', methods=['GET'])
def getGameStep(gameId: str):
    # TODO: step forward and backward? Maybe play the whole game first or in parallel?
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not valid.')

        mm: MatchManager = app.games[gameId]

        curr = mm.nextPlayerDict()
        mm.nextStep()
        nxt = mm.nextPlayerDict()

        lastAction = None
        lastOutcome = None

        if not mm.update and len(mm.actions_history) > 0:
            lastAction = mm.actions_history[-1]
            lastOutcome = mm.outcome[-1]

        logger.info(f'Restored game #{gameId} with scenario {mm.board.name}')

        return jsonify({
            'gameId': gameId,
            'state': mm.state,
            'meta': {
                'curr': {
                    'step': curr['step'],
                    'player': curr['player'],
                    'interactive': curr['isHuman'],
                },
                'next': {
                    'step': nxt['step'],
                    'player': nxt['player'],
                    'interactive': nxt['isHuman'],
                },
                'end': mm.end,
                'winner': mm.winner,
                'update': mm.update,
                'action': lastAction,
                'outcome': lastOutcome,
                'interactive': mm.humans,
            }
        }), 200

    except ValueError as ve:
        logger.error(ve)
        return jsonify({
            'error': str(ve),
        }), 400


@main.route('/api/game/action/<gameId>', methods=['POST'])
def postGameAction(gameId: str):
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not valid.')

        mm: MatchManager = app.games[gameId]

        logger.info(request.content_type)
        logger.info(request.get_json(force=True))

        data: dict = request.json
        team = data['team']

        player: Agent = mm.getPlayer(team)

        if not isinstance(player, Human):
            raise ValueError('Action for not an interactive player')

        player.nextAction(mm.board, mm.state, data)

        return getGameStep(gameId)

    except Exception as e:
        logger.error(e)
        return jsonify({
            'error': str(e),
        }), 400


@main.route('/api/game/board/<gameId>')
def getGameBoard(gameId: str):
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not valid.')

        mm: MatchManager = app.games[gameId]

        logger.info(f'Restored game #{gameId} with scenario {mm.board.name}')

        return jsonify({
            'board': mm.board,
            'gameId': gameId,
        }), 200

    except ValueError as ve:
        logger.error(ve)
        return jsonify({
            'error': str(ve),
        }), 400


@main.route('/api/game/state/<gameId>')
def getGameState(gameId: str):
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not registered')

        mm: MatchManager = app.games[gameId]
        nxt = mm.nextPlayerDict()

        logger.info(f'Restored game #{gameId} with scenario {mm.board.name}')

        return jsonify({
            'gameId': gameId,
            'state': mm.state,
            'meta': {
                'next': {
                    'step': nxt['step'],
                    'player': nxt['player'],
                    'interactive': nxt['isHuman'],
                },
                'end': mm.end,
                'winner': mm.winner,
                'update': mm.update,
                'interactive': mm.humans,
            }
        }), 200

    except ValueError as ve:
        logger.error(ve)
        return jsonify({
            'error': str(ve),
        }), 400

# TODO: add endpoints to get a list of possible actions for team (too many?!) or for figure
