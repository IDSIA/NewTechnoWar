import numpy as np

from core import RED, BLUE, Terrain, hitScoreCalculator
from core.actions import Action, Move, Shoot, Respond, DoNothing
from core.figures import Figure, StatusType, FigureType, missMatrixRed, missMatrixBlue
from core.game.board import GameBoard
from core.weapons import Weapon
from utils.coordinates import cube_reachable, to_hex, cube_to_hex, cube_linedraw

MISS_MATRIX = {
    RED: missMatrixRed,
    BLUE: missMatrixBlue
}


class GameManager:
    """
    State of the board of the game.
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        # static properties of the board
        self.board = GameBoard(shape)
        self.obstacles = set()

        # support set
        self.turn = 0

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            RED: [],
            BLUE: []
        }

    # operations on board layout (static properties)

    def addTerrain(self, terrain: np.array):
        """
        Sum a terrain matrix to the current board.
        The values must be of core.Terrain Types.
        Default '0' is 'open ground'.
        """
        self.board.terrain += terrain

    def addGeography(self, geography: np.array):
        """Sum a geography matrix to the current board"""
        self.board.geography += geography

    def addObjective(self, objective: np.array):
        """Sum an objective matrix to the current board"""
        self.board.objective += objective

    # operations on figures (dynamic properties)

    def addFigure(self, agent: str, figure: Figure):
        """
        Add a figures to the units of the given agent and it setup the index
        in the matrix at the position of the figure.
        """
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

    def activableFigures(self, agent: str):
        """Returns a list of figures that have not been activated."""
        # TODO:
        #   transform this in an array that is restored at the beginning of the turn with
        #   the activable figures, when a figure is activated, remove it from such array
        return [f for f in self.figures[agent] if not f.activated]

    def canActivate(self, agent: str):
        """Returns True if there are still figures that can be activated."""
        return len(self.activableFigures(agent)) > 0

    def canShoot(self, weapon: Weapon, target: Figure, n: int, nObstacles: int):
        canHit = weapon.curved or nObstacles == 0
        hasAmmo = weapon.hasAmmo()
        available = weapon.isAvailable()
        isInRange = weapon.max_range >= n

        # TODO: verify that I can use anti-tank against non-vehicles
        if weapon.antitank:
            # can shoot only against vehicles
            validTarget = target.kind == FigureType.VEHICLE
        else:
            # can shoot against infantry and others only
            validTarget = target.kind < FigureType.VEHICLE

        return all([canHit, hasAmmo, available, isInRange, validTarget])

    def buildMovements(self, agent: str, figure: Figure):
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""

        distance = figure.move - figure.load
        obstacles = self.board.getObstacleSet()

        for f in self.figures[RED]:
            obstacles.add(f.position)
        for f in self.figures[BLUE]:
            obstacles.add(f.position)

        # TODO: add movement enhanced on roads

        # TODO: move all cube functions to a single conversion point
        movements = cube_reachable(figure.position, distance, obstacles)

        return [Move(agent, figure, m) for m in movements]

    def buildShoots(self, agent: str, figure: Figure):
        """Returns a list of all the possible shooting actions that can be performed."""

        tAgent = RED if agent == BLUE else BLUE
        shoots = []

        for target in self.figures[tAgent]:
            terrain = self.board.getHexagon(to_hex(target.position)).terrain

            los = cube_linedraw(figure.position, target.position)
            obstacles = [self.board.getHexagon(cube_to_hex(h)).terrain > Terrain.ROAD for h in los]
            nObstacles = len(obstacles)
            n = len(los)

            for weapon in figure.weapons:
                if self.canShoot(weapon, target, n, nObstacles):
                    shoots.append(Shoot(agent, figure, target, weapon, terrain, los))

        return shoots

    def buildResponses(self, agent: str, figure: Figure):
        """Returns a list of all possible response action that can be performed."""

        responses = []

        if figure.canRespond:
            target = figure.attackedBy
            terrain = self.board.getHexagon(to_hex(target.position)).terrain

            los = cube_linedraw(figure.position, target.position)
            obstacles = [self.board.getHexagon(cube_to_hex(h)).terrain > Terrain.ROAD for h in los]
            nObstacles = len(obstacles)
            n = len(los)

            for weapon in figure.weapons:
                if weapon.canShoot(target, n, nObstacles):
                    responses.append(Respond(agent, figure, target, weapon, terrain, los))

        return responses

    def buildActionForFigure(self, agent: str, figure: Figure):
        """Build all possible actions for the given figure."""
        actions = []

        for movement in self.buildMovements(agent, figure):
            actions.append(movement)

        for shoot in self.buildShoots(agent, figure):
            actions.append(shoot)

        for response in self.buildResponses(agent, figure):
            actions.append(response)

        return actions

    def buildActions(self, agent: str):
        """
        Build a list with all the possible actions that can be executed by an agent
        with the current status of the board.
        """
        actions = []

        self.obstacles = self.board.getObstacleSet()

        for figure in self.figures[agent]:
            for action in self.buildActionForFigure(agent, figure):
                actions.append(action)

        return actions

    def activate(self, action: Action):
        """Apply the given action to the map."""
        action.figure.activated = True
        agent = action.agent

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
            los: list = action.los

            # TODO: curved weapons (mortar) have different hit computation

            # consume ammunition
            w.shoot()

            score = np.random.choice(range(1, 21), size=w.dices)

            # shoot/response
            if isinstance(action, Respond):
                ATK = w.atk_response
                INT = f.get_INT_DEF(self.turn)
            else:
                ATK = w.atk_normal
                INT = f.get_INT_ATK(self.turn)

            # TODO: smoke rule:
            #       if you fire against a panzer, and during the line of sight, you meet a smoke hexagon (not only on
            #       the hexagon where the panzer is), this smoke protection is used, and not the basis one.

            # anti-tank rule
            if w.antitank and t.kind == FigureType.VEHICLE:
                DEF = 0
            else:
                DEF = t.defense['basic']

            TER = o.protection_level
            STAT = f.get_STAT().value
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
                # TODO: choose which weapon to disable
                # TODO: if zero, remove when update
            elif w.curved:
                # mortar
                v = np.random.choice(range(1, 21), size=1)
                hitLocation = MISS_MATRIX[agent](v)
                # TODO: use hit matrix
                pass

    def update(self):
        """End turn function that updates the status of all figures and moves forward the internal turn ticker."""
        self.turn += 1

        for agent in [RED, BLUE]:
            for figure in self.figures[agent]:
                # TODO: compute there cutoff status?
                figure.set_STAT(StatusType.NO_EFFECT)
                figure.activated = False
                figure.responded = False
                figure.attackedBy = None
                if figure.hp <= 0:
                    figure.killed = True

        # TODO: remove killed unit?

    def whoWon(self) -> int:
        """
        Check whether either side has won the game and return the winner:
            None = 0
            RED = 1
            BLUE = 2
        """
        # TODO: this should be something related to the scenario
        goals = self.board.getGoals()

        for agent in [RED, BLUE]:
            for figure in self.figures[agent]:
                if figure.position in goals:
                    if agent == RED:
                        return 1
                    else:
                        return 2

        return 0

    def hashValue(self) -> int:
        """Encode the current state of the game (board positions) as an integer."""

        # positive numbers are RED figures, negatives are BLUE figures
        m = (self.board.figures[RED] + 1) - (self.board.figures[BLUE] + 1)

        return hash(str(m))
