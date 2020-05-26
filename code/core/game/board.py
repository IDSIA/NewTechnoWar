import numpy as np

from core import Terrain, FigureType, TERRAIN_TYPE, TERRAIN_OBSTACLES_TO_LOS, RED, BLUE
from core.figures import Figure
from utils.coordinates import to_cube, Cube, cube_neighbor, cube_to_hex


class GameBoard:
    """
    Static parts of the game board.
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # matrices filled with -1 so we can use 0-based as index
        self.terrain = np.zeros(shape, dtype='uint8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')

        # contains the figure at the given position: pos -> [figure, ...]
        self.posToFigure = {
            RED: dict(),
            BLUE: dict(),
        }

        x, y = shape

        self.limits = \
            [to_cube((q, -1)) for q in range(-1, y + 1)] + \
            [to_cube((q, y)) for q in range(-1, y + 1)] + \
            [to_cube((-1, r)) for r in range(0, y)] + \
            [to_cube((x, r)) for r in range(0, y)]

        # obstructions to LOS
        self.obstacles = set(self.limits)

        # movement obstructions are considered in the cost
        self.moveCost = {
            FigureType.INFANTRY: np.zeros(shape, dtype='float'),
            FigureType.VEHICLE: np.zeros(shape, dtype='float'),
        }

        self.protectionLevel = np.zeros(shape, dtype='uint8')

    # operations on board layout (static properties)

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

                if index in TERRAIN_OBSTACLES_TO_LOS:
                    self.obstacles.update(to_cube((i, j)))

    def addGeography(self, geography: np.array):
        """Sum a geography matrix to the current board"""
        self.geography += geography

    def addObjective(self, objective: np.array):
        """Sum an objective matrix to the current board"""
        self.objective += objective

    # operations on graph

    def getNeighbors(self, position: Cube):
        return [n for n in cube_neighbor(position) if n not in self.limits]

    def getMovementCost(self, end: Cube, kind: int):
        pos = cube_to_hex(end)
        if pos in self.posToFigure[RED] and self.posToFigure[RED][pos].kind == FigureType.VEHICLE:
            return 1000.0
        if pos in self.posToFigure[BLUE] and self.posToFigure[BLUE][pos].kind == FigureType.VEHICLE:
            return 1000.0
        return self.moveCost[kind][pos]

    def moveFigure(self, agent: str, figure: Figure, curr: Cube = None, dst: Cube = None):
        """Moves a figure from current position to another destination."""
        ptf = self.posToFigure[agent]
        if curr:
            ptf[curr].remove(figure)
            if len(ptf[curr]) == 0:
                ptf.pop(curr, None)
        if dst:
            if dst not in ptf:
                ptf[dst] = list()
            ptf[dst].append(figure)
            figure.goto(dst)

    def getFigureByPos(self, agent: str, pos: tuple) -> list:
        if len(pos) == 2:
            pos = to_cube(pos)
        if pos not in self.posToFigure[agent]:
            return []
        return self.posToFigure[agent][pos]

    def getProtectionLevel(self, pos: Cube):
        return self.protectionLevel[cube_to_hex(pos)]

    def isObstacle(self, pos: Cube) -> bool:
        if pos in self.obstacles:
            return True

        i = 0
        for agent in (RED, BLUE):
            for f in self.getFigureByPos(agent, pos):
                if f.kind == FigureType.VEHICLE:
                    i += 1

        return i > 0

    def getGoals(self):
        """Returns the position marked as goals"""
        goals = np.argwhere(self.objective > 0)
        return set(map(to_cube, goals))
