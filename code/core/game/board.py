from typing import Dict, Set, Tuple, List

import numpy as np

from core.const import RED, BLUE
from core.figures import FigureType
from core.game.goals import Goal, GoalReachPoint
from core.game.terrain import TERRAIN_TYPE
from utils.coordinates import to_cube, Cube, cube_neighbor, cube_to_hex, cube_range


class GameBoard:
    """
    Static parts of the game board.
    """
    __slots__ = ['name', 'shape', 'terrain', 'geography', 'objectives', 'limits', 'obstacles', 'moveCost',
                 'protectionLevel']

    def __init__(self, shape: Tuple[int, int], name: str = ''):
        self.name: str = name
        self.shape: Tuple[int, int] = shape

        # matrices filled with -1 so we can use 0-based as index
        self.terrain: np.ndarray = np.zeros(shape, dtype='uint8')
        self.geography: np.ndarray = np.zeros(shape, dtype='uint8')

        self.objectives: dict = {RED: [], BLUE: []}

        x, y = shape

        self.limits: Set[Cube] = set(
            [to_cube((q, -1)) for q in range(-1, y + 1)] +
            [to_cube((q, y)) for q in range(-1, y + 1)] +
            [to_cube((-1, r)) for r in range(0, y)] +
            [to_cube((x, r)) for r in range(0, y)]
        )

        # obstructions to LOS
        self.obstacles: Set[Cube] = set()

        # movement obstructions are considered in the cost
        self.moveCost: Dict[int, np.ndarray] = {
            FigureType.INFANTRY: np.zeros(shape, dtype='float'),
            FigureType.VEHICLE: np.zeros(shape, dtype='float'),
        }

        self.protectionLevel: np.ndarray = np.zeros(shape, dtype='uint8')

        # internal values initialization
        self.addTerrain(self.terrain)

    def addTerrain(self, terrain: np.array):
        """
        Sum a terrain matrix to the current board. The values must be of core.Terrain Types.
        Default '0' is 'open ground'.
        """
        self.terrain += terrain

        x, y = self.shape

        # update movement costs, protection level and obstacles
        for i in range(0, x):
            for j in range(0, y):
                index = self.terrain[i, j]
                tt = TERRAIN_TYPE[index]
                self.protectionLevel[i, j] = tt.protectionLevel
                self.moveCost[FigureType.INFANTRY][i, j] = tt.moveCostInf
                self.moveCost[FigureType.VEHICLE][i, j] = tt.moveCostVehicle

                if tt.blockLos:
                    self.obstacles.add(to_cube((i, j)))

    def addGeography(self, geography: np.array):
        """Add a geography matrix to the current board."""
        self.geography += geography

    def addObjectives(self, *objectives: Goal):
        """Add the objectives for the given team to the current board."""
        for objective in objectives:
            self.objectives[objective.team].append(objective)

    def getObjectives(self, team: str = None):
        """Returns the goals for the team."""
        return self.objectives[team]

    def getObjectivesPositions(self, team: str = None) -> List[Cube]:
        """Returns a list with the positions referred by the objectives with a point as goal (i.e. GoalReachPoint)."""
        objs = []
        for x in self.objectives[team]:
            if isinstance(x, GoalReachPoint):
                objs += x.objectives

        return objs

    def getObjectiveMark(self):
        """Return the position of all objectives in the map."""
        marks = []
        for team in [RED, BLUE]:
            for o in self.objectives[team]:
                if isinstance(o, GoalReachPoint):
                    marks += o.objectives
        return marks

    def getNeighbors(self, position: Cube):
        """Returns all the neighbors of the given position."""
        return [n for n in cube_neighbor(position) if n not in self.limits]

    def getMovementCost(self, pos: Cube, kind: int):
        """Returns the cost of move in the given position."""
        try:
            h = cube_to_hex(pos)
            if 0 <= h.q < self.shape[0] and 0 <= h.r < self.shape[1]:
                return self.moveCost[kind][h]
            raise IndexError('Outside map!')
        except IndexError as _:
            return 1000.0
        except KeyError as _:
            return 1000.0

    def getProtectionLevel(self, pos: Cube):
        """Returns the protection level in the given position."""
        return self.protectionLevel[cube_to_hex(pos)]

    def isObstacle(self, pos: Cube) -> bool:
        """Return if the given position is an obstacle or not."""
        return pos in self.obstacles

    def getRange(self, center: Cube, n: int):
        """Returns all the positions inside a given range and a center."""
        r = []
        for x in cube_range(center, n):
            h = cube_to_hex(x)
            if 0 < h.q < self.shape[0] and 0 < h.r < self.shape[1]:
                r.append(x)
        return r
