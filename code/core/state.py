import numpy as np

from core import RED, BLUE, Terrain, hit_score_calculator
from core.figures import Figure, Infantry, Tank
from core.weapons import Weapon
from core.actions import Action, Move, Shoot  # , Respond

from utils.coordinates import Hex, Cube, cube_reachable, to_cube, to_hex, cube_to_hex, cube_linedraw


class Hexagon:

    def __init__(self, hex: Hex, pos: tuple, terrain, geography, objective, figure):
        self.hex = hex
        self.pos = pos
        self.terrain = terrain
        self.objective = objective > 0
        self.figure = figure

    def isObstructed(self):
        return self.terrain > Terrain.ROAD


class Board:
    """
    Static parts of the board
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # matrices filled with -1 so we can use 0-based as index
        # self.obstacles = np.zeros(shape, dtype='uint8')
        self.terrain = np.zeros(shape, dtype='int8')
        # self.roads = np.zeros(shape, dtype='uint8')
        self.geography = np.zeros(shape, dtype='uint8')
        self.objective = np.zeros(shape, dtype='uint8')
        self.figures = {
            RED: np.full(shape, -1, dtype='int8'),
            BLUE: np.full(shape, -1, dtype='int8'),
        }

        x, y = shape

        self.limits = \
            [to_cube((q, -1)) for q in range(-1, y + 1)] + \
            [to_cube((q, y)) for q in range(-1, y + 1)] + \
            [to_cube((-1, r)) for r in range(0, y)] + \
            [to_cube((x, r)) for r in range(0, y)]

    def moveFigure(self, agent: str, index: int, curr: Cube = None, dst: Cube = None):
        """
        Moves a figure from current position to another destination.
        """
        if curr:
            self.figures[agent][cube_to_hex(curr)] = -1
        if dst:
            self.figures[agent][cube_to_hex(dst)] = index

    def getHexagon(self, pos: tuple):
        """
        Return the Hexagon descriptor object at the given position.
        """
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

    def getObstacleSet(self):
        """
        Returns a set of all obstacles. Obstacls are considered:
            - limit of the map
            - obstacles added to the map
        """
        obs = np.argwhere(self.terrain[self.terrain > Terrain.ROAD])
        return set([to_cube(o) for o in obs] + self.limits)


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
        self.turn = 0  # TODO: increase turn

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            RED: [],
            BLUE: []
        }

    # operations on board layout (static properties)

    # def addObstacle(self, obstacles: np.array):
        # """Sum an obstacle matrix to the current board"""
        # self.board.obstacles += obstacles

    def addTerrain(self, terrain: np.array):
        """
        Sum a terrain matrix to the current board.
        The values must be of core.Terrain Types.
        Default '0' is 'open ground'.
        """
        self.board.terrain += terrain

    # def addRoads(self, roads: np.array):
        # """Sum a road matrix to the current board"""
        # self.board.roads += roads

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

        # obstacles = np.zeros(self.shape, dtype='uint8')
        # obstacles[(4, 4)] = 1
        # self.addObstacle(obstacles)

        # roads = np.zeros(self.shape, dtype='uint8')
        # roads[0, :] = 1
        # self.addRoads(roads)

        terrain = np.zeros(self.shape, dtype='uint8')
        terrain[(4, 4)] = 1
        terrain[0, :] = Terrain.ROAD
        self.addTerrain(terrain)

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

    def buildMovements(self, agent: str, figure: Figure):
        """
        Build all the movement actions for a figure. All the other units are
        considered as obstacles.
        """

        distance = figure.move - figure.load
        obstacles = self.obstacles.copy()

        for f in self.figures[RED]:
            obstacles.add(f.position)
        for f in self.figures[BLUE]:
            obstacles.add(f.position)

        """
        # TODO: add movement enhanced on roads
        max_distance = distance
        if (figure.kind == FigureType.INFANTRY):
            max_distance += 1
        elif (figure.kind == FigureType.VEHICLE):
            max_distance += 2
        # TODO: consider terrain type for obstacles
        """

        movements = cube_reachable(figure.position, distance, obstacles)

        return [Move(agent, figure, m) for m in movements]

    def buildShoots(self, agent: str, figure: Figure):
        """
        """

        tAgent = RED if agent == BLUE else BLUE
        shoots = []

        for target in self.figures[tAgent]:
            los = cube_linedraw(figure.position, target.position)
            if any({self.board.getHexagon(cube_to_hex(h)).terrain > Terrain.ROAD for h in los}):
                continue

            terrain = self.board.getHexagon(to_hex(target.position))
            n = len(los)

            for weapon in figure.equipment:
                if n <= weapon.max_range:
                    shoots.append(Shoot(agent, figure, target, weapon, terrain))

        return shoots

    def buildActionForFigure(self, agent: str, figure: Figure):
        """
        Build all possible actions for a single figure.
        """
        actions = []

        for movement in self.buildMovements(agent, figure):
            actions.append(movement)

        for shoot in self.buildShoots(agent, figure):
            actions.append(shoot)
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
        """
        Apply the given action to the map.
        """
        action.figure.activated = True

        # TODO: perform action with figure
        if isinstance(action, Move):
            self.board.moveFigure(action.agent, action.figure.index, action.figure.position, action.destination)
            action.figure.goto(action.destination)

        if isinstance(action, Shoot):
            f: Figure = action.figure
            t: Figure = action.target
            w: Weapon = action.weapon
            o: Terrain = action.terrain

            score = max(np.random.choice(range(1, 21), size=w.dices))

            # TODO: defense should be baed on army
            hitScore = hit_score_calculator(w.atk_normal, o.protection_level, t.defense['basic'], f.get_STAT(), f.get_END(self.turn), f.get_INT_ATK(self.turn))

            print(f'{action.agent}\tSHOOT {t}({o}) with {f} using {w} ({score}/{hitScore})')

            if score <= hitScore:
                t.hp -= 1
                print(f'{action.agent}\tSHOOT {f} hit {w}')
                # TODO: if zero, remove when update

    def update(self):
        self.turn += 1
        # TODO: reset unit status (activated, STAT on terrain, response)
        # TODO: remove killed unit

    def canRespond(self, team: str):
        # TODO:
        return False

    def goalAchieved(self):
        # TODO:
        return False
