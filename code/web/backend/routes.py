import logging
import os
import random
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify, redirect, send_file
from flask import current_app as app
from flask_cors import CORS

from agents import  Agent, Human, MatchManager, buildMatchManager
from core.const import BLUE, RED
from core.templates import *
from web.backend.images import board2png, scenario2png
from web.backend.utils import scroll, fieldShape, cube_to_ijxy, pzoneToHex, pos_to_dict

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})


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


@main.route('/config', methods=['GET'])
def config():
    """Serve a list of available configuration object"""
    try:
        collect()

        return make_response(
            render_template(
                'config.html',
                title='Game | NewTechnoWar',
                template='game-template',
                data={
                    'weapons': TMPL_WEAPONS,
                    'figures': TMPL_FIGURES,
                    'status': TMPL_FIGURES_STATUS_TYPE,
                    'terrain': TMPL_TERRAIN_TYPE,
                    'boards': TMPL_BOARDS,
                    'scenarios': TMPL_SCENARIOS
                }
            )
        )

    except ValueError as ve:
        logger.error(ve)
        return redirect('/')


@main.route('/config/map/<name>', methods=['GET'])
def configMap(name: str):
    if '/' in name or '\\' in name or '.' in name:
        logger.warning(f'invalid map name! {name}')
        return ''

    logger.info(f'serving map for {name}')

    filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
    board2png(filename, name)

    return send_file(filename, mimetype='image/png')


@main.route('/config/scenario/<name>', methods=['GET'])
def configScenario(name: str):
    if '/' in name or '\\' in name or '.' in name:
        logger.warning(f'invalid map name! {name}')
        return ''

    logger.info(f'serving scenario for {name}')

    filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
    scenario2png(filename, name)

    return send_file(filename, mimetype='image/png')


def checkGameId() -> (str, MatchManager):
    if 'gameId' not in request.cookies:
        raise ValueError('GameId is missing!')

    gameId = request.cookies['gameId']

    if gameId not in app.games:
        raise ValueError('GameId not registered')

    mm: MatchManager = app.games[gameId]

    return gameId, mm


@main.route('/game/', methods=['GET'])
# TODO: deprecated, remove this
def game():
    """Serve game main page."""

    try:
        gameId, mm = checkGameId()

        logger.info(f'Restored game #{gameId} with scenario {mm.board.name}')

        # compute view box size and zoom (default is: 0, 0, 400, 300)
        eps = 20
        min_x, min_y, max_x, max_y = 1000000, 1000000, 0, 0
        for team in [RED, BLUE]:
            for figure in mm.state.figures[team]:
                _, _, x, y = cube_to_ijxy(figure.position)

                min_x = min(min_x, x - eps)
                min_y = min(min_y, y - eps)
                max_x = max(max_x, x + eps)
                max_y = max(max_y, y + eps)

            if mm.state.has_choice[team]:
                for color in mm.state.choices[team]:
                    for figure in mm.state.choices[team][color]:
                        _, _, x, y = cube_to_ijxy(figure.position)

                        min_x = min(min_x, x - eps)
                        min_y = min(min_y, y - eps)
                        max_x = max(max_x, x + eps)
                        max_y = max(max_y, y + eps)

        w = max(max_x - min_x, 400)
        h = max(max_y - min_y, 300)

        pzRed = None
        pzBlue = None
        if mm.state.has_placement[RED]:
            pzRed = mm.state.placement_zone[RED] if RED in mm.state.placement_zone else None
        if mm.state.has_placement[BLUE]:
            pzBlue = mm.state.placement_zone[BLUE] if BLUE in mm.state.placement_zone else None

        response = make_response(
            render_template(
                'game.html',
                title='Game | NewTechnoWar',
                template='game-template',
                board=list(scroll(mm.board)),
                gameId=gameId,
                shape=fieldShape(mm.board),
                turn=mm.state.turn,
                vb=(min_x, min_y, w, h),
                pzRed=list(pzoneToHex(pzRed)),
                pzBlue=list(pzoneToHex(pzBlue)),
            )
        )

        response.set_cookie('gameId', gameId)
        return response

    except ValueError as ve:
        logger.error(ve)
        return redirect('/')


@main.route('/game/reset', methods=['GET'])
# TODO: deprecated, remove this
def gameReset():
    try:
        _, mm = checkGameId()
        mm.reset()

        response = make_response(
            redirect(f'/game/')
        )

        return response

    except ValueError as ve:
        logger.error(ve)
        return redirect('/')


@main.route('/game/state', methods=['GET'])
# TODO: deprecated, remove this
def gameState():
    logger.info('Request state')

    try:
        _, mm = checkGameId()
        return jsonify({
            'state': mm.state,
            'params': app.params[mm.gid],
            'next': mm.nextPlayerDict(),
            'humans': mm.humans,
        }), 200

    except ValueError as e:
        logger.error(e)
        return None, 404


@main.route('/game/next/step', methods=['GET'])
# TODO: deprecated, remove this
def gameNextStep():
    logger.debug('Request next')

    try:
        _, mm = checkGameId()
        curr = mm.nextPlayerDict()
        mm.nextStep()
        nxt = mm.nextPlayerDict()

        lastAction = None
        lastOutcome = None

        if not mm.update:
            lastAction = mm.actions_history[-1]
            lastOutcome = mm.outcome[-1]

        return jsonify({
            'end': mm.end,
            'winner': mm.winner,
            'update': mm.update,
            'state': mm.state,
            'action': lastAction,
            'outcome': lastOutcome,
            'curr': curr,
            'next': nxt,
            'humans': mm.humans,
        }), 200

    except ValueError as e:
        logger.error(e)
        return None, 404


@main.route('/game/human/click', methods=['POST'])
# TODO: deprecated, remove this
def gameHumanClick():
    gameId, mm = checkGameId()

    data = request.form
    team = data['team']

    try:
        player: Agent = mm.getPlayer(team)
        if not isinstance(player, Human):
            raise ValueError('player is not controllable')
        player.nextAction(mm.board, mm.state, data)

        ret = {}
        if data['action'] == 'place':
            i = int(data['x'])
            j = int(data['y'])
            ret = pos_to_dict(i, j)
            ret['team'] = team

        return jsonify(ret), 200

    except ValueError as e:
        logger.exception(f'Human click error: {e}')
        return jsonify({'error': str(e)}), 403


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
        redPlayer = 'GreedyAgent'
        bluePlayer = 'GreedyAgent'
        scenario = 'Junction'
        autoplay = True
        seed = 0
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


@main.route('/api/game/step/<gameId>', methods=['POST'])
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
def getGameAction(gameId: str):
    try:
        if not gameId:
            raise ValueError('GameId is missing!')

        if gameId not in app.games:
            raise ValueError('GameId not valid.')

        mm: MatchManager = app.games[gameId]

        data: dict = request.json
        team = data['team']

        player: Agent = mm.getPlayer(team)

        if not isinstance(player, Human):
            raise ValueError('Action for not an interactive player')

        player.nextAction(mm.board, mm.state, data)

        # TODO: return something informative

        return gameNextStep(gameId)

    except ValueError as ve:
        logger.error(ve)
        return jsonify({
            'error': str(ve),
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
