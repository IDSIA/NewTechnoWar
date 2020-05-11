import numpy as np

from core import RED, BLUE, Terrain, hitScoreCalculator
from core.figures import Figure, Infantry, Tank, StatusType, FigureType
from core.weapons import Weapon
from core.actions import Action, Move, Shoot, Respond, DoNothing

from utils.coordinates import Hex, Cube, cube_reachable, to_cube, to_hex, cube_to_hex, cube_linedraw


class Hexagon:
    """
    Description of a single Hexagon.
    """

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
    Static parts of the board.
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

    def getObstacleSet(self):
        """
        Returns a set of all obstacles. Obstacls are considered:
            - limit of the map
            - obstacles added to the map
        """
        obs = np.argwhere(self.terrain > Terrain.ROAD)
        return set([to_cube(o) for o in obs] + self.limits)


class StateOfTheBoard:
    """
    State of the board of the game.
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # static properties of the board
        self.board = Board(shape)

        # support set
        self.turn = 0

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
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""

        distance = figure.move - figure.load
        obstacles = self.board.getObstacleSet()

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
        """

        movements = cube_reachable(figure.position, distance, obstacles)

        return [Move(agent, figure, m) for m in movements]

    def buildShoots(self, agent: str, figure: Figure):
        """Returns a list of all the possible shooting actions that can be performed."""

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

    def buildResponse(self, agent: str, figure: Figure):
        """Returns a list of all possible response action that can be performed."""

        responses = []

        if figure.canRespond:
            target = figure.attackedBy
            los = cube_linedraw(figure.position, target.position)
            if any({self.board.getHexagon(cube_to_hex(h)).terrain > Terrain.ROAD for h in los}):
                return responses

            terrain = self.board.getHexagon(to_hex(target.position))
            n = len(los)

            for weapon in figure.weapons:
                if n <= weapon.max_range:
                    responses.append(Respond(agent, figure, target, weapon, terrain))
        return responses

    def buildActionForFigure(self, agent: str, figure: Figure):
        """Build all possible actions for the given figure."""
        actions = []

        for movement in self.buildMovements(agent, figure):
            actions.append(movement)

        for shoot in self.buildShoots(agent, figure):
            actions.append(shoot)

        for response in self.buildResponse(agent, figure):
            actions.append(response)

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
        """Apply the given action to the map."""
        action.figure.activated = True

        print(action)

        if isinstance(action, DoNothing):
            return

        if isinstance(action, Move):
            self.board.moveFigure(action.agent, action.figure.index, action.figure.position, action.destination)
            action.figure.goto(action.destination)
            action.figure.set_STAT(StatusType.IN_MOTION)

        if isinstance(action, Shoot):  # Respond *is* a shoot action
            f: Figure = action.figure
            t: Figure = action.target
            w: Weapon = action.weapon
            o: Terrain = action.terrain

            # TODO: curved weapons (mortar) have different hit computation

            score = np.random.choice(range(1, 21), size=w.dices)

            # shoot/response
            if isinstance(action, Respond):
                ATK = w.atk_response
                INT = f.get_INT_DEF(self.turn)
            else:
                ATK = w.atk_normal
                INT = f.get_INT_ATK(self.turn)

            # anti-tank rule
            if w.antitank and t.kind == FigureType.VEHICLE:
                DEF = 0
            else:
                DEF = t.defense['basic']

            TER = o.protection_level
            STAT = f.get_STAT(self.turn)
            END = f.get_END(self.turn)

            hitScore = hitScoreCalculator(ATK, TER, DEF, STAT, END, INT)

            success = len([x for x in score if x <= hitScore])

            # target status changes for the _next_ hit
            t.set_STAT(StatusType.UNDER_FIRE)
            # target can now respond to the fire
            t.canRespond(f)

            print(f'{action.agent}\tSHOOT {t}({o}) with {f} using {w} (({success}) {score}/{hitScore})')

            if success > 0:
                t.hp -= success
                print(f'{action.agent}\tSHOOT {f} hit {w}')
                # TODO: if zero, remove when update

    def update(self):
        """End turn function that updates the status of all figures and moves forward the internal turn ticker."""
        self.turn += 1

        for agent in [RED, BLUE]:
            for figure in self.figures[agent]:
                # TODO: compute there cutoff status?
                figure.set_STAT(StatusType.NO_EFFECT)
                figure.activated = False
                figure.canRespond = False
                figure.attackedBy = None
                if figure.hp <= 0:
                    figure.killed = True

        # TODO: remove killed unit?

    def goalAchieved(self):
        # TODO:
        return False
