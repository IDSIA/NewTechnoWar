import numpy as np

from core.figures import Figure, Infantry, Tank, TYPE_VEHICLE, TYPE_INFANTRY
from core.actions import Action, Move, Shoot, Respond
from utils.coordinates import Hex, cube_reachable, to_cube, to_hex
from utils.colors import red, blue, yellow, green, pinkBg, grayBg
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

        self.obstacles = np.zeros(shape, dtype='uint8')
        self.terrain = np.zeros(shape, dtype='uint8')
        self.roads = np.zeros(shape, dtype='uint8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')
        self.figures = {
            RED: np.zeros(shape, dtype='uint8'),
            BLUE: np.zeros(shape, dtype='uint8'),
        }

    def getHexagon(self, pos: tuple = None, hex: hex = None):
        if pos:
            hex = to_hex(pos)
        elif hex:
            pos = tuple(hex)
        return Hexagon(
            hex,
            pos,
            obstacle=self.obstacle[pos],
            terrain=TERRAIN_LEVEL_OF_PROTECTION[self.terrain[pos]],
            road=self.road[pos] > 0,
            objective=self.objective[pos] > 0,
            figure={
                RED: self.figures[RED][pos],
                BLUE: self.figures[BLUE][pos]
            })

    def getObstacleSet(self):
        # tuples = self.obstacles.nonzero()
        # obs = np.array([tuples[1], tuples[0]]).T

        obs = np.array(self.obstacles.nonzero()).T
        return set([to_cube(o) for o in obs])


class StateOfTheBoard:
    """
    State of the board of the game
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # static properties of the board
        self.board = Board(shape)

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            RED: [None],
            BLUE: [None]
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
        index = len(figures)

        figures.append(figure)
        figure.index = index
        self.board.figures[agent][figure.position] = index

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

        self.addFigure(self.red, Infantry(position=(1, 1), name='rInf1'))
        self.addFigure(self.red, Tank(position=(1, 2), name='rTank1'))
        self.addFigure(self.blue, Infantry(position=(3, 3), name='bInf1'))

    def activableFigures(self, team: str):
        """Returns a list of figures that have not been activated."""
        # TODO:
        #   transform this in an array that is restored at the beginning of the turn with
        #   the activable figures, when a figure is activated, remove it from such array
        return [f for f in self.figures[team] if not f.activated]

    def canActivate(self, team: str):
        """Returns True if there are still figures that can be activated."""
        return len(self.activableFigures(team)) > 0

    def buildActions(self, team: str):
        """Build a list with all the possible actions that can be executed by an agent with the current status of the board."""
        actions = []

        obstacles = self.board.getObstacleSet()

        for figure in self.figures[team]:

            # build movement actions

            distance = figure.move - figure.load

            max_distance = distance
            if (figure.kind == TYPE_INFANTRY):
                max_distance += 1
            elif (figure.kind == TYPE_VEHICLE):
                max_distance += 2

            movements = cube_reachable(figure.cube, distance, obstacles)

            for movement in movements:
                # apply road rules
                # TODO
                set([self.board.getHexagon(hex)])

                actions.append(Move(figure, movement))

        return actions

    def activate(self, action: Action):
        # TODO: perform action with figure
        pass

    def canRespond(self, team: str):
        # TODO:
        return False

    def goalAchieved(self):
        # TODO:
        return False

    def print(self, size=3, extra: list = None):
        cols, rows = self.shape

        board_extra = np.zeros(self.shape, dtype='uint8')

        if extra:
            for e in extra:
                board_extra[e] = 1

        sep_horizontal = '+'.join(['-' * size] * cols)

        print('+' + '|'.join([f' {c} ' for c in range(0, rows)]), '+')
        print('+' + sep_horizontal + '+')

        for r in range(rows):
            line = []
            for c in range(cols):
                p = (c, r)
                cell = [' '] * size

                if self.board.objective[p] > 0:
                    cell[1] = yellow('x')

                if board_extra[p] > 0:
                    cell[0] = green('x')

                redFigure = self.board.figures[RED][p]
                if redFigure > 0:
                    figure = self.getFigureByPos(RED, (c, r))

                    cell[1] = red('T') if figure.kind == TYPE_VEHICLE else red('I')

                blueFigure = self.board.figures[BLUE][p]
                if blueFigure > 0:
                    figure = self.getFigureByPos(BLUE, (c, r))

                    cell[1] = blue('T') if figure.kind == TYPE_VEHICLE else blue('I')

                if self.board.obstacles[p] > 0:
                    cell = [pinkBg(c) for c in cell]
                if self.board.roads[p] > 0:
                    cell = [grayBg(c) for c in cell]

                line.append(''.join(cell))

            print('|' + '|'.join([l for l in line] + [f' {r}']))
        print('+' + sep_horizontal + '+')
