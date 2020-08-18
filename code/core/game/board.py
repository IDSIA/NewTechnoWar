import numpy as np

from core.figures import FigureType
from core.game.terrain import TERRAIN_TYPE
from utils.coordinates import to_cube, Cube, cube_neighbor, cube_to_hex, cube_range


class GameBoard:
    """
    Static parts of the game board.
    """

    __slots__ = ['name', 'shape', 'terrain', 'geography', 'objective', 'limits', 'obstacles', 'moveCost',
                 'protectionLevel']

    def __init__(self, shape: tuple, name: str = ''):
        self.name = name
        self.shape = shape

        # matrices filled with -1 so we can use 0-based as index
        self.terrain = np.zeros(shape, dtype='uint8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')

        x, y = shape

        self.limits = set(
            [to_cube((q, -1)) for q in range(-1, y + 1)] +
            [to_cube((q, y)) for q in range(-1, y + 1)] +
            [to_cube((-1, r)) for r in range(0, y)] +
            [to_cube((x, r)) for r in range(0, y)]
        )

        # obstructions to LOS
        self.obstacles = set()

        # movement obstructions are considered in the cost
        self.moveCost = {
            FigureType.INFANTRY: np.zeros(shape, dtype='float'),
            FigureType.VEHICLE: np.zeros(shape, dtype='float'),
        }

        self.protectionLevel = np.zeros(shape, dtype='uint8')

    def addTerrain(self, terrain: np.array):
        """
        Sum a terrain matrix to the current board.
        The values must be of core.Terrain Types.
        Default '0' is 'open ground'.
        """
        self.terrain += terrain

        x, y = self.shape

        # update movement costs, protection level and obstacles
        for i in range(0, x):
            for j in range(0, y):
                index = terrain[i, j]
                tt = TERRAIN_TYPE[index]
                self.protectionLevel[i, j] = tt.protectionLevel
                self.moveCost[FigureType.INFANTRY][i, j] = tt.moveCostInf
                self.moveCost[FigureType.VEHICLE][i, j] = tt.moveCostVehicle

                if tt.blockLos:
                    self.obstacles.add(to_cube((i, j)))

    def addGeography(self, geography: np.array):
        """Add a geography matrix to the current board."""
        self.geography += geography

    def addObjective(self, objective: np.array):
        """Add an objective matrix to the current board."""
        self.objective += objective

    def getNeighbors(self, position: Cube):
        """Returns all the neighbors of the given position."""
        return [n for n in cube_neighbor(position) if n not in self.limits]

    def getMovementCost(self, pos: Cube, kind: int):
        """Returns the cost of move in the given position."""
        if pos in self.limits:
            return 1000.0

        cost = self.moveCost[kind]

        if pos not in cost:
            return 1000.0

        return cost[cube_to_hex(pos)]

    def getProtectionLevel(self, pos: Cube):
        """Returns the protection level in the given position."""
        return self.protectionLevel[cube_to_hex(pos)]

    def isObstacle(self, pos: Cube) -> bool:
        """Return if the given position is an obstacle or not."""
        if pos in self.obstacles:
            return True

    def getGoals(self):
        """Returns the positions marked as goals."""
        goals = np.argwhere(self.objective > 0)
        return set(map(to_cube, goals))

    def getRange(self, center: Cube, n: int):
        """Returns all the positions inside a given range and a center."""
        r = []
        for x in cube_range(center, n):
            h = cube_to_hex(x)
            if 0 < h.q < self.shape[0] and 0 < h.r < self.shape[1]:
                r.append(x)
        return r
