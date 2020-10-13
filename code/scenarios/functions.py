import numpy as np

from core.const import RED, BLUE
from core.figures import Weapon, FIGURES_STATUS_TYPE, Figure
from core.game.board import GameBoard
from core.game.goals import GoalEliminateOpponent, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.game.state import GameState
from core.game.terrain import TERRAIN_TYPE
from core.templates import TMPL_WEAPONS, TMPL_BOARDS, TMPL_SCENARIOS, TMPL_FIGURES
from scenarios.utils import fillLine, parse_slice
from utils import INFINITE


def setup_weapons(figure: Figure, values: dict) -> None:
    for wName, wData in values.items():
        tw = TMPL_WEAPONS[wName]
        tw['ammo'] = INFINITE if wData == 'inf' else wData
        tw['ammo_max'] = tw['ammo']

        w = Weapon()
        for kw, vw in tw.items():
            if kw == 'atk':
                setattr(w, 'atk_normal', vw['normal'])
                setattr(w, 'atk_response', vw['response'])
            else:
                setattr(w, kw, vw)
        figure.addWeapon(w)


def parseBoard(name: str) -> GameBoard:
    bData = TMPL_BOARDS[name]
    shape = tuple(bData['shape'])
    board = GameBoard(shape, name)

    terrain = np.full(shape, TERRAIN_TYPE[bData['default']].level, dtype='uint8')

    for tName, tData in bData['terrain'].items():
        level = TERRAIN_TYPE[tName].level
        for elem in tData:
            if 'line' in elem:
                l = elem['line']
                fillLine(terrain, (l[0], l[1]), (l[2], l[3]), level)
            if 'region' in elem:
                start, end = elem['region'].split(',')
                terrain[parse_slice(start), parse_slice(end)] = level
            if 'row_alternate' in elem:
                low, high = elem['row_alternate']
                for i in range(board.shape[0]):
                    j = low if i % 2 == 0 else high
                    terrain[i, j] = level

    board.addTerrain(terrain)

    return board


def buildScenario(name: str) -> (GameBoard, GameState):
    template = TMPL_SCENARIOS[name]

    board: GameBoard = parseBoard(template['map'])
    state: GameState = GameState(board.shape, name)
    if 'turn' in template:
        state.turn = template['turn'] - 2  # turns are 0-based and there is 1 initialization update

    for team in [RED, BLUE]:
        if 'placement' in template[team]:
            placement_zone = np.zeros(board.shape, dtype='uint8')

            for elem in template[team]['placement']:
                if 'region' in elem:
                    start, end = elem['region'].split(',')
                    placement_zone[parse_slice(start), parse_slice(end)] = 1

            state.addPlacementZone(team, placement_zone)

        for o, v in template[team]['objectives'].items():
            # setup objectives
            other = BLUE if team == RED else RED
            obj = None

            if o == 'eliminate_opponent':
                obj = GoalEliminateOpponent(team, other)
            if o == 'reach_point':
                v = [tuple(w) for w in v]
                obj = GoalReachPoint(team, board.shape, v)
            if o == 'defend_point':
                v = [tuple(w) for w in v]
                obj = GoalDefendPoint(team, other, board.shape, v)
            if o == 'max_turn':
                obj = GoalMaxTurn(team, v)

            if obj:
                board.addObjectives(obj)

        for f in template[team]['figures']:
            # setup figures
            colors = {}
            for fName, fData in f.items():
                s = FIGURES_STATUS_TYPE[fData['status']] if 'status' in fData else FIGURES_STATUS_TYPE['NO_EFFECT']
                t = TMPL_FIGURES[fData['type']]
                figure = Figure(fData['position'], fName, team, t['kind'], s)

                # setup colors
                color = t.get('color', None)
                if color:
                    if color not in colors:
                        colors[color] = []
                    colors[color].append(figure)

                for k, v in t.items():
                    if k == 'weapons':
                        setup_weapons(figure, v)

                    elif k == 'loaded':
                        # parse loaded figures
                        for lName, lData in v.items():
                            lt = TMPL_FIGURES[lData['type']]
                            lFigure = Figure(fData['position'], lName, team, lt['kind'])
                            figure.transportLoad(lFigure)
                            for lk, lv in lt.items():
                                if lk == 'weapons':
                                    setup_weapons(lFigure, lv)
                                else:
                                    setattr(lFigure, lk, lv)

                    else:
                        setattr(figure, k, v)

                state.addFigure(figure)

            for color, figures in colors.items():
                state.addChoice(team, color, *figures)

    return board, state
