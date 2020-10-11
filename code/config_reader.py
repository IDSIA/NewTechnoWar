import os
import yaml
import numpy as np
from collections.abc import Mapping

from core.const import BLUE, RED
from core.figures import Figure, Weapon
from core.figures.status import HIDDEN, LOADED, NO_EFFECT, IN_MOTION, UPSTAIRS, UNDER_FIRE, CUT_OFF
from core.game.board import GameBoard
from core.game.goals import GoalEliminateOpponent, GoalDefendPoint, GoalMaxTurn, GoalReachPoint
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import fillLine
from utils import INFINITE
from utils.copy import deepcopy

WEAPONS_TMPL = {}
FIGURES_TMPL = {}
FIGURES_TYPE = {'other': 0, 'infantry': 1, 'vehicle': 2}
FIGURES_STATUS_TYPE = {
    'HIDDEN': HIDDEN,
    'LOADED': LOADED,
    'NO_EFFECT': NO_EFFECT,
    'IN_MOTION': IN_MOTION,
    'UPSTAIRS': UPSTAIRS,
    'UNDER_FIRE': UNDER_FIRE,
    'CUT_OFF': CUT_OFF,
}
TERRAIN_TYPE = {}
BOARDS = {}
SCENARIOS = {}


def parse_figure(data: dict):
    for name, fData in data['figure'].items():
        FIGURES_TMPL[name] = fData


def parse_weapons(data: dict):
    for name, wData in data['weapon'].items():
        WEAPONS_TMPL[name] = wData


def parse_terrain(data: dict):
    for name, tData in data['terrain'].items():
        TERRAIN_TYPE[name] = Terrain(
            len(TERRAIN_TYPE),
            tData['name'],
            tData['protection'],
            tData['move_cost']['infantry'],
            tData['move_cost']['vehicle'],
            tData['block_los']
        )


def parse_board(data: dict):
    for name, bData in data['board'].items():
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


def update(d: dict, u: Mapping):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def parse_scenario(data: dict):
    for name, sData in data['scenario'].items():
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
                    s = FIGURES_STATUS_TYPE[fData['status']] if 'status' in fData else NO_EFFECT
                    t = update(deepcopy(FIGURES_TMPL['template']), FIGURES_TMPL[fData['type']])
                    t['kind'] = FIGURES_TYPE[t.pop('type', None)]
                    t['hp_max'] = t['hp']

                    figure = Figure(fData['position'], name, team, t['kind'], s)
                    for k, v in t.items():
                        if k == 'weapons':
                            # setup weapons
                            for wName, wData in v.items():
                                tw = update(deepcopy(WEAPONS_TMPL['template']), WEAPONS_TMPL[wName])
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

    dirs = ['terrains', 'maps', 'weapons', 'figures', 'scenarios']

    for dir in dirs:
        path = os.path.join('config', dir)
        for name in os.listdir(path):
            with open(os.path.join(path, name)) as f:
                data = yaml.safe_load(f)

                if 'terrain' in data:
                    parse_terrain(data)

                if 'board' in data:
                    parse_board(data)

                if 'weapon' in data:
                    parse_weapons(data)

                if 'figure' in data:
                    parse_figure(data)

                if 'scenario' in data:
                    parse_scenario(data)

    for name, scenario in SCENARIOS.items():
        board, state = scenario
        print(name)
        print(board)
        print(state)
