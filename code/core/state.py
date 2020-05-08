import numpy as np

from core.figures import Figure, Infantry, Tank
from core.actions import Action, Move  # , Shoot, Respond
from utils.coordinates import Hex, Cube, cube_reachable, to_cube, to_hex, cube_to_hex
from core import RED, BLUE, TERRAIN_LEVEL_OF_PROTECTION


class Hexagon:

    def __init__(self, hex: Hex, pos: tuple, obstacle, terrain, road, geography, objective, figure):
        self.hex = hex
        self.pos = pos
        self.obstacle = obstacle
        self.terrain = terrain
        self.road = road
        self.objective = objective
        self.figure = figure


class Board:
    """
    Static parts of the board
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # matrices filled with -1 so we can use 0-based as index
        self.obstacles = np.zeros(shape, dtype='uint8')
        self.terrain = np.full(shape, -1, dtype='int8')
        self.roads = np.zeros(shape, dtype='uint8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')
        self.figures = {
            RED: np.full(shape, -1, dtype='int8'),
            BLUE: np.full(shape, -1, dtype='int8'),
        }

    def moveFigure(self, agent: str, index: int, curr: Cube = None, dst: Cube = None):
        if curr:
            self.figures[agent][cube_to_hex(curr)] = -1
        if dst:
            self.figures[agent][cube_to_hex(dst)] = index

    def getHexagon(self, pos: tuple = None, hex: hex = None):
        if pos:
            hex = to_hex(pos)
        elif hex:
            pos = tuple(hex)
        return Hexagon(
            hex,
            pos,
            obstacle=self.obstacles[pos],
            terrain=TERRAIN_LEVEL_OF_PROTECTION[self.terrain[pos]],
            road=self.roads[pos] > 0,
            geography=self.geography[pos],
            objective=self.objective[pos] > 0,
            figure={
                RED: self.figures[RED][pos],
                BLUE: self.figures[BLUE][pos]
            })

    def getObstacleSet(self):
        obs = np.array(self.obstacles.nonzero()).T.tolist()
        return set([to_cube(o) for o in obs])


class StateOfTheBoard:
    """
    State of the board of the game
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # static properties of the board
        self.board = Board(shape)

        # support set
        self.obstacles = set()

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            RED: [],
            BLUE: []
        }

    # operations on board layout (static properties)

    def addObstacle(self, obstacles: np.array):
        """Sum an obstacle matrix to the current board"""
        self.board.obstacles += obstacles

    def addTerrain(self, terrain: np.array):
        """Sum a terrain matrix to the current board"""
        self.board.terrain += terrain

    def addRoads(self, roads: np.array):
        """Sum a road matrix to the current board"""
        self.board.roads += roads

    def addGeography(self, geography: np.array):
        """Sum a geography matrix to the current board"""
        self.board.geography += geography

    def addObjective(self, objective: np.array):
        """Sum an objective matrix to the current board"""
        self.board.objective += objective

    # operations on figures (dynamic properties)

    def addFigure(self, agent: str, figure: Figure):
        """Add a figures to the units of the given agent and it setup the index in the matric at the position of the figure."""
        figures = self.figures[agent]
        index = len(figures)  # to have 0-based index

        figures.append(figure)
        figure.index = index
        self.board.moveFigure(agent, index, dst=figure.position)

    def getFigureByIndex(self, agent: str, index: int):
        """Given an index of a figure, return the figure."""
        return self.figures[agent][index]

    def getFigureByPos(self, agent: str, pos: tuple):
        """Given a position of a figure, return the figure."""
        index = self.board.figures[agent][pos]
        return self.getFigureByIndex(agent, index)

    # other operations

    def resetScenario1(self):
        """
        Sets up a specific scenario. reset to state of board to an initial state.
        Here this is just a dummy.
        """
        # TODO: make StateOfTheBoard abstract, with "reset" method abstract and implement it in a new class

        obstacles = np.zeros(self.shape, dtype='uint8')
        obstacles[(4, 4)] = 1
        self.addObstacle(obstacles)

        roads = np.zeros(self.shape, dtype='uint8')
        roads[0, :] = 1
        self.addRoads(roads)

        objective = np.zeros(self.shape, dtype='uint8')
        objective[4, 5] = 1
        self.addObjective(objective)

        self.addFigure(RED, Infantry(position=(1, 1), name='rInf1'))
        self.addFigure(RED, Tank(position=(1, 2), name='rTank1'))
        self.addFigure(BLUE, Infantry(position=(3, 3), name='bInf1'))

    def activableFigures(self, agent: str):
        """Returns a list of figures that have not been activated."""
        # TODO:
        #   transform this in an array that is restored at the beginning of the turn with
        #   the activable figures, when a figure is activated, remove it from such array
        return [f for f in self.figures[agent] if not f.activated]

    def canActivate(self, agent: str):
        """Returns True if there are still figures that can be activated."""
        return len(self.activableFigures(agent)) > 0

    def _buildMovementActions(self, figure, obstacles):
        # build movement actions

        distance = figure.move - figure.load

        """
            # TODO: add movement enhanced on roads
            max_distance = distance
            if (figure.kind == FigureType.INFANTRY):
                max_distance += 1
            elif (figure.kind == FigureType.VEHICLE):
                max_distance += 2
            """

        movements = cube_reachable(figure.position, distance, obstacles)
        return movements

    def buildActionForFigure(self, agent: str, figure: Figure):
        actions = []
        # TODO: obstacles could be more dynamic
        for movement in self._buildMovementActions(figure, self.obstacles):
            actions.append(Move(agent, figure, movement))
        return actions

    def buildActions(self, agent: str):
        """Build a list with all the possible actions that can be executed by an agent with the current status of the board."""
        actions = []

        self.obstacles = self.board.getObstacleSet()

        for figure in self.figures[agent]:
            for action in self.buildActionForFigure(agent, figure):
                actions.append(action)

        return actions

    def activate(self, action: Action):
        action.figure.activated = True

        # TODO: perform action with figure
        if isinstance(action, Move):
            self.board.moveFigure(action.agent, action.figure.index, action.figure.position, action.destination)
            action.figure.goto(action.destination)

    def canRespond(self, team: str):
        # TODO:
        return False

    def goalAchieved(self):
        # TODO:
        return False
