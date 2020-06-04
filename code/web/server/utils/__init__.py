from core import Terrain, TERRAIN_OBSTACLES_TO_LOS, TERRAIN_TYPE
from core.game import GameBoard
from utils.coordinates import to_cube


class Hexagon:
    def __init__(self, position: tuple, terrain: Terrain, geography: int, objective: bool, obstacle: bool):
        self.terrain = terrain
        self.geography = geography
        self.objective = objective
        self.obstacle = obstacle
        self.position = position
        self.cube = to_cube(position)

        i, j = position

        if i % 2 == 0:
            self.x = 10 + 15 * i
            self.y = 18 + 18 * j
        else:
            self.x = 10 + 15 * i
            self.y = 9 + 18 * j

    def css(self):
        csss = ['terrOpen', 'terrRoad', 'terrTree', 'terrForest', 'terrUrban', 'terrBuilding', 'terrWooden',
                'terrConcrete']

        for i in range(len(csss)):
            if self.terrain == TERRAIN_TYPE[i]:
                return csss[i]

        return ''


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
                tt in TERRAIN_OBSTACLES_TO_LOS,
            )

            yield h
