import numpy as np

from core import Terrain, RED, BLUE
from utils.coordinates import Hex, to_cube, Cube, cube_neighbor, cube_to_hex


class Hexagon:
    """
    Description of a single Hexagon.
    """

    def __init__(self, hex: Hex, pos: tuple, terrain, geography, objective, figure):
        self.hex = hex
        self.pos = pos
        self.terrain = terrain
        self.geography = geography
        self.objective = objective > 0
        self.figure = figure

    def isObstructed(self):
        return self.terrain > Terrain.ROAD


class GameBoard:
    """
    Static parts of the game board.
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # matrices filled with -1 so we can use 0-based as index
        self.terrain = np.zeros(shape, dtype='int8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')

        # convert to list of matrices, one for each figure
        self.figures = {
            RED: np.full(shape, -1, dtype='uint8'),
            BLUE: np.full(shape, -1, dtype='uint8'),
        }

        x, y = shape

        self.limits = \
            [to_cube((q, -1)) for q in range(-1, y + 1)] + \
            [to_cube((q, y)) for q in range(-1, y + 1)] + \
            [to_cube((-1, r)) for r in range(0, y)] + \
            [to_cube((x, r)) for r in range(0, y)]

    def getNeighbors(self, position: Cube):
        obs = self.getObstacleSet()  # TODO:cache this
        return [n for n in cube_neighbor(position) if n not in obs]

    def getCost(self, start: Cube, end: Cube):
        terrainStart = self.terrain[cube_to_hex(start)]
        terrainEnd = self.terrain[cube_to_hex(end)]

        # TODO: model movement on city for vehicles
        if terrainStart == terrainEnd and terrainStart == 1:
            return 0.75  # ROAD
        return 1

    def moveFigure(self, agent: str, index: int, curr: Cube = None, dst: Cube = None):
        """Moves a figure from current position to another destination."""
        if curr:
            self.figures[agent][cube_to_hex(curr)] = -1
        if dst:
            self.figures[agent][cube_to_hex(dst)] = index

    def getHexagon(self, pos: tuple):
        """Return the Hexagon descriptor object at the given position."""
        return Hexagon(
            to_cube(pos),
            pos,
            terrain=self.terrain[pos],
            geography=self.geography[pos],
            objective=self.objective[pos] > 0,
            figure={
                RED: self.figures[RED][pos],
                BLUE: self.figures[BLUE][pos]
            })

    def getObstacleSet(self) -> set:
        """
        Returns a set of all obstacles. Obstacls are considered:
            - limit of the map
            - obstacles added to the map
        """
        obs = np.argwhere(self.terrain > Terrain.ROAD)
        s = set(map(to_cube, obs))
        s.update(self.limits)
        return s

    def getGoals(self):
        """Returns the position marked as goals"""
        goals = np.argwhere(self.objective > 0)
        return set(map(to_cube, goals))
