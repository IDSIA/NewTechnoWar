from math import sqrt

from core import Terrain, TERRAIN_TYPE
from core.game import GameBoard
from utils.coordinates import to_cube

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

    print(f'{i:2} {j:2} -> {x:3} {y:3}')

    return x, y


class Hexagon:
    def __init__(self, position: tuple, terrain: Terrain, geography: int, objective: bool, blockLos: bool):
        self.terrain = terrain
        self.geography = geography
        self.objective = objective
        self.blockLos = blockLos
        self.position = position
        self.cube = to_cube(position)

        self.x, self.y = pos_to_xy(position)

    def css(self):
        csss = ['terrOpen', 'terrRoad', 'terrTree', 'terrForest', 'terrUrban', 'terrBuilding', 'terrWooden',
                'terrConcrete']

        for i in range(len(csss)):
            if self.terrain == TERRAIN_TYPE[i]:
                return csss[i]

        return ''


def fieldShape(board: GameBoard):
    x, y = board.shape
    return (x + 3/4) * w, (y + 1/2) * h


def scroll(board: GameBoard):
    x, y = board.shape

    for i in range(0, x):
        for j in range(0, y):
            p = (i, j)

            index = board.terrain[p]
            tt = TERRAIN_TYPE[index]

            h = Hexagon(
                p,
                tt,
                board.geography[p],
                board.objective[p] > 0,
                tt.blockLos
            )

            yield h