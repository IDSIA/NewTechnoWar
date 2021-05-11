from math import sqrt

import numpy as np

from core.game.board import GameBoard
from core.game.terrain import Terrain, TYPE_TERRAIN, TERRAIN_TYPE
from core.utils.coordinates import Cube, Hex

SIZE = 10
w = SIZE * 2
h = SIZE * sqrt(3)


def pos_to_xy(position: tuple) -> tuple:
    i, j = position

    x = w / 2 + 3 / 4 * w * i

    if i % 2 == 0:
        y = h + h * j
    else:
        y = h / 2 + h * j

    return x, y


def pos_to_dict(i: int, j: int) -> dict:
    x, y = pos_to_xy((i, j))
    return {'i': i, 'j': j, 'x': x, 'y': y}


def cube_to_ijxy(position: Cube) -> tuple:
    i, j = position.tuple()
    x, y = pos_to_xy((i, j))
    return i, j, x, y


def cube_to_dict(position: Cube) -> dict:
    i, j = position.tuple()
    x, y = pos_to_xy((i, j))
    return {'i': i, 'j': j, 'x': x, 'y': y}


class Hexagon:
    def __init__(self, position: Hex, terrain: Terrain, geography: int, objective: bool, blockLos: bool,
                 color: str = 'white'):
        self.terrain = terrain
        self.geography = geography
        self.objective = objective
        self.blockLos = blockLos
        self.cube = position.cube()
        self.color = color

        self.i, self.j = position.tuple()
        self.x, self.y = pos_to_xy((self.i, self.j))

    def css(self) -> str:
        csss = ['terrOpen', 'terrRoad', 'terrTree', 'terrForest', 'terrUrban', 'terrBuilding', 'terrWooden',
                'terrConcrete']

        for i in range(len(csss)):
            if self.terrain == TYPE_TERRAIN[i]:
                return csss[i]

        return ''


def fieldShape(board: GameBoard) -> tuple:
    x, y = board.shape
    return (x + 3 / 4) * w, (y + 1 / 2) * h


def scroll(board: GameBoard):
    x, y = board.shape

    objectiveMarks = board.getObjectiveMark()

    for i in range(0, x):
        for j in range(0, y):
            p = Hex(i, j)
            x = p.tuple()

            index = board.terrain[x]
            tt = TYPE_TERRAIN[index]

            h = Hexagon(
                p,
                tt,
                board.geography[x],
                p.cube() in objectiveMarks,
                tt.blockLos,
                tt.color
            )

            yield h


def pzoneToHex(zone):
    if zone is None:
        return []

    x, y = np.where(zone > 0)

    for item in zip(x, y):
        h = Hexagon(
            Hex(t=item),
            TERRAIN_TYPE['OPEN_GROUND'],
            0,
            False,
            False
        )

        yield h