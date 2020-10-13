from math import sqrt
import numpy as np

from core.game.terrain import Terrain, TYPE_TERRAIN, TERRAIN_TYPE
from core.game.board import GameBoard
from utils.coordinates import to_cube, cube_to_hex

SIZE = 10
w = SIZE * 2
h = SIZE * sqrt(3)


def pos_to_xy(position):
    i, j = position

    x = w / 2 + 3 / 4 * w * i

    if i % 2 == 0:
        y = h + h * j
    else:
        y = h / 2 + h * j

    return x, y


def pos_to_dict(i, j):
    x, y = pos_to_xy((i, j))
    return {'i': i, 'j': j, 'x': x, 'y': y}


def cube_to_ijxy(position):
    i, j = cube_to_hex(position)
    x, y = pos_to_xy((i, j))
    return i, j, x, y


def cube_to_dict(position):
    i, j = cube_to_hex(position)
    x, y = pos_to_xy((i, j))
    return {'i': i, 'j': j, 'x': x, 'y': y}


class Hexagon:
    def __init__(self, position: tuple, terrain: Terrain, geography: int, objective: bool, blockLos: bool):
        self.terrain = terrain
        self.geography = geography
        self.objective = objective
        self.blockLos = blockLos
        self.cube = to_cube(position)

        self.i, self.j = position
        self.x, self.y = pos_to_xy(position)

    def css(self):
        csss = ['terrOpen', 'terrRoad', 'terrTree', 'terrForest', 'terrUrban', 'terrBuilding', 'terrWooden',
                'terrConcrete']

        for i in range(len(csss)):
            if self.terrain == TYPE_TERRAIN[i]:
                return csss[i]

        return ''


def fieldShape(board: GameBoard):
    x, y = board.shape
    return (x + 3 / 4) * w, (y + 1 / 2) * h


def scroll(board: GameBoard):
    x, y = board.shape

    objectiveMarks = board.getObjectiveMark()

    for i in range(0, x):
        for j in range(0, y):
            p = (i, j)

            index = board.terrain[p]
            tt = TYPE_TERRAIN[index]

            h = Hexagon(
                p,
                tt,
                board.geography[p],
                to_cube(p) in objectiveMarks,
                tt.blockLos
            )

            yield h


def pzoneToHex(zone):
    if zone is None:
        return []

    x, y = np.where(zone > 0)

    for item in zip(x, y):
        h = Hexagon(
            item,
            TERRAIN_TYPE['OPEN_GROUND'],
            0,
            False,
            False
        )

        yield h
