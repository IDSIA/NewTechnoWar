import numpy as np

from core.const import BLUE, RED
from core.figures import Figure, Weapon
from core.figures.status import FigureStatus
from core.game.board import GameBoard
from core.game.goals import GoalEliminateOpponent, GoalDefendPoint, GoalMaxTurn, GoalReachPoint
from core.game.state import GameState
from core.game.terrain import Terrain
from core.templates import *
from scenarios.utils import fillLine
from utils import INFINITE

FIGURES_TYPE = {'other': 0, 'infantry': 1, 'vehicle': 2}
FIGURES_STATUS_TYPE = {}

TERRAIN_TYPE = {}
BOARDS = {}
SCENARIOS = {}


def parse_figure_status():
    for fName, fData in TMPL_FIGURES_STATUS_TYPE.items():
        FIGURES_STATUS_TYPE[fName] = FigureStatus(fData['name'], fData['value'])


def parse_terrain():
    for name, tData in TMPL_TERRAIN_TYPE.items():
        TERRAIN_TYPE[name] = Terrain(
            len(TERRAIN_TYPE),
            tData['name'],
            tData['protection'],
            tData['move_cost']['infantry'],
            tData['move_cost']['vehicle'],
            tData['block_los']
        )


def parse_board():
    for name, bData in TMPL_BOARDS.items():
        shape = tuple(bData['shape'])

        board = GameBoard(shape, name)
        BOARDS[name] = board

        terrain = np.full(shape, TERRAIN_TYPE[bData['default']].level, dtype='uint8')
        board.addTerrain(terrain)

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


# def update(d: dict, u: Mapping):
#     for k, v in u.items():
#         if isinstance(v, Mapping):
#             d[k] = update(d.get(k, {}), v)
#         else:
#             d[k] = v
#     return d


def parse_slice(value: str) -> slice:
    """
    Parses a `slice()` from string, like `start:stop:step`.
    """
    value = value.strip()
    if value:
        parts = value.split(':')
        if len(parts) == 1:
            # slice(stop)
            parts = [None, parts[0]]
        # else: slice(start, stop[, step])
    else:
        # slice()
        parts = []
    return slice(*[int(p) if p else None for p in parts])


def parse_scenario():
    for fName, sData in TMPL_SCENARIOS.items():
        # if 'template' in sData:
        #     sData = update(deepcopy(TMPL_SCENARIOS[sData['template']]), sData)

        board: GameBoard = BOARDS[sData['map']]
        state: GameState = GameState(board.shape, fName)
        if 'turn' in sData:
            state.turn = sData['turn'] - 2  # turns are 0-based and there is 1 initialization update

        SCENARIOS[fName] = (board, state)

        for team in [RED, BLUE]:
            if 'placement' in sData[team]:
                placement_zone = np.zeros(board.shape, dtype='uint8')

                for elem in sData[team]['placement']:
                    if 'region' in elem:
                        start, end = elem['region'].split(',')
                        placement_zone[parse_slice(start), parse_slice(end)] = 1

                state.addPlacementZone(team, placement_zone)

            for o, v in sData[team]['objectives'].items():
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

            for f in sData[team]['figures']:
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

                        if k == 'loaded':
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


# def update_figure_template(fData):
#     t = update(deepcopy(TMPL_FIGURES['template']), TMPL_FIGURES[fData['type']])
#     t['kind'] = FIGURES_TYPE[t.pop('type', None)]
#     t['hp_max'] = t['hp']
#     return t


def setup_weapons(figure, values):
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


if __name__ == '__main__':
    parse_figure_status()
    parse_terrain()
    parse_board()
    parse_scenario()

    for name, scenario in SCENARIOS.items():
        board, state = scenario
        print(name)
        print(board)
        print(state)
