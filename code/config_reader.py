import os
import yaml
import numpy as np

from core.game.board import GameBoard
from core.game.terrain import Terrain
from scenarios.utils import fillLine

TERRAIN_TYPE = {}
BOARDS = []


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
        shape = bData['shape']

        board = GameBoard(shape, name)
        BOARDS.append(board)

        terrain = np.zeros(shape, dtype='uint8')
        for ttype, tdata in bData['terrain'].items():
            t = TERRAIN_TYPE[ttype]
            for elem in tdata:
                if 'line' in elem:
                    fillLine(terrain, elem['line'][0], elem['line'][1], t.level)
                if 'point' in elem:
                    terrain[elem['point']] = t.level

        board.addTerrain(terrain)


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

    print(BOARDS[0].terrain)
