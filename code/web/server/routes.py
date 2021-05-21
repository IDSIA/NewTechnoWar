import logging
import os
import random
import uuid

from flask import Blueprint, render_template, make_response, request, jsonify, redirect, send_file
from flask import current_app as app

from agents import Human, MatchManager, buildMatchManager
from core.const import BLUE, RED
from core.templates import *
from utils.images import board2png, scenario2png
from web.server.utils import scroll, fieldShape, cube_to_ijxy, pzoneToHex, pos_to_dict

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main.route('/', methods=['GET', 'POST'])
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

        collect()
        scenarios = [k for k, v in TMPL_SCENARIOS.items() if 'offline' not in v]

        players = [
            'Human',
            'RandomAgent',
            'GreedyAgent',
            'AlphaBetaAgent',
            'AlphaBetaFast1Agent',
        ]

        response = make_response(
            render_template(
                'index.html',
                title='Home | NewTechnoWar',
                template='game-template',
                scenarios=scenarios,
                players=players
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
def gameHumanClick():
    gameId, mm = checkGameId()

    data = request.form
    team = data['team']

    try:
        player: Human = mm.getPlayer(team)
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
