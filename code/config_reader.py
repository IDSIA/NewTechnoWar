import os
import yaml
import numpy as np
from collections.abc import Mapping

from core.const import BLUE, RED
from core.figures import Figure, Weapon
from core.figures.status import FigureStatus
from core.game.board import GameBoard
from core.game.goals import GoalEliminateOpponent, GoalDefendPoint, GoalMaxTurn, GoalReachPoint
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import fillLine
from utils import INFINITE
from utils.copy import deepcopy

TMPL_WEAPONS = {}
TMPL_FIGURES = {}
TMPL_FIGURES_STATUS_TYPE = {}
TMPL_TERRAIN_TYPE = {}
TMPL_BOARDS = {}
TMPL_SCENARIOS = {}

FIGURES_TYPE = {'other': 0, 'infantry': 1, 'vehicle': 2}
FIGURES_STATUS_TYPE = {}

TERRAIN_TYPE = {}
BOARDS = {}
SCENARIOS = {}


def collect_figure_status(data: dict):
    for name, fData in data['status'].items():
        TMPL_FIGURES_STATUS_TYPE[name] = fData


def parse_figure_status():
    for name, fData in TMPL_FIGURES_STATUS_TYPE.items():
        FIGURES_STATUS_TYPE[name] = FigureStatus(fData['name'], fData['value'])


def collect_figure(data: dict):
    for name, fData in data['figure'].items():
        TMPL_FIGURES[name] = fData


def collect_weapons(data: dict):
    for name, wData in data['weapon'].items():
        TMPL_WEAPONS[name] = wData


def collect_terrain(data: dict):
    for name, tData in data['terrain'].items():
        TMPL_TERRAIN_TYPE[name] = tData


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


def collect_board(data: dict):
    for name, bData in data['board'].items():
        TMPL_BOARDS[name] = bData


def parse_board():
    for name, bData in TMPL_BOARDS.items():
        if 'template' in bData:
            bData = update(deepcopy(TMPL_BOARDS[bData['template']]), bData)

        shape = tuple(bData['shape'])

        board = GameBoard(shape, name)
        BOARDS[name] = board

        terrain = np.full(shape, TERRAIN_TYPE[bData['default']].level, dtype='uint8')
        board.addTerrain(terrain)

        for ttype, tdata in bData['terrain'].items():
            t = TERRAIN_TYPE[ttype]
            for elem in tdata:
                if 'line' in elem:
                    fillLine(terrain, elem['line'][0], elem['line'][1], t.level)
                if 'point' in elem:
                    terrain[elem['point']] = t.level
                if 'column' in elem:
                    c = elem['column']
                    if isinstance(c, Mapping):
                        if 'start' in c and 'end' not in c:
                            terrain[c['start']:, :] = t.level
                        elif 'start' not in c and 'end' in c:
                            terrain[:c['end'], :] = t.level
                        elif 'start' in c and 'end' in c:
                            terrain[c['start']:c['end'], :] = t.level
                    else:
                        terrain[c, :] = t.level

                if 'row' in elem:
                    r = elem['row']
                    if isinstance(r, Mapping):
                        if 'start' in r and 'end' not in r:
                            terrain[:, r['start']:] = t.level
                        elif 'start' not in r and 'end' in r:
                            terrain[:, r['end']] = t.level
                        elif 'start' in r and 'end' in r:
                            terrain[:, r['start']:r['end']] = t.level
                    else:
                        terrain[:, r] = t.level


def update(d: dict, u: Mapping):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def collect_scenario(data: dict):
    for name, sData in data['scenario'].items():
        TMPL_SCENARIOS[name] = sData


def parse_scenario():
    for name, sData in TMPL_SCENARIOS.items():
        board: GameBoard = BOARDS[sData['map']]
        state: GameState = GameState(board.shape, name)

        SCENARIOS[name] = (board, state)

        for team in [RED, BLUE]:
            for o, v in sData[team]['objectives'].items():
                # setup objectives
                other = BLUE if team == RED else RED
                obj = None

                if o == 'eliminate_opponent':
                    obj = GoalEliminateOpponent(team, other)
                if o == 'reach_point':
                    v = [tuple(l) for l in v]
                    obj = GoalReachPoint(team, board.shape, v)
                if o == 'defend_point':
                    v = [tuple(l) for l in v]
                    obj = GoalDefendPoint(team, other, board.shape, v)
                if o == 'max_turn':
                    obj = GoalMaxTurn(team, v)

                if obj:
                    board.addObjectives(obj)

            for f in sData[team]['figures']:
                # setup figures
                for name, fData in f.items():
                    s = FIGURES_STATUS_TYPE[fData['status']] if 'status' in fData else FIGURES_STATUS_TYPE['NO_EFFECT']
                    t = update(deepcopy(TMPL_FIGURES['template']), TMPL_FIGURES[fData['type']])
                    t['kind'] = FIGURES_TYPE[t.pop('type', None)]
                    t['hp_max'] = t['hp']

                    figure = Figure(fData['position'], name, team, t['kind'], s)
                    for k, v in t.items():
                        if k == 'weapons':
                            # setup weapons
                            for wName, wData in v.items():
                                tw = update(deepcopy(TMPL_WEAPONS['template']), TMPL_WEAPONS[wName])
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

                        else:
                            setattr(figure, k, v)

                    state.addFigure(figure)


if __name__ == '__main__':

    dirs = ['terrains', 'maps', 'weapons', 'status', 'figures', 'scenarios']

    # TODO: first collect, then parse
    for dir in dirs:
        path = os.path.join('config', dir)
        for name in os.listdir(path):
            with open(os.path.join(path, name)) as f:
                data = yaml.safe_load(f)

                if 'terrain' in data:
                    collect_terrain(data)

                if 'board' in data:
                    collect_board(data)

                if 'weapon' in data:
                    collect_weapons(data)

                if 'status' in data:
                    collect_figure_status(data)

                if 'figure' in data:
                    collect_figure(data)

                if 'scenario' in data:
                    collect_scenario(data)

    parse_figure_status()
    parse_terrain()
    parse_board()
    parse_scenario()

    for name, scenario in SCENARIOS.items():
        board, state = scenario
        print(name)
        print(board)
        print(state)
