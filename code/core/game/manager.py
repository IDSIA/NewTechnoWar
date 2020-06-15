import logging

import numpy as np

from core import RED, BLUE, FigureType
from core.actions import Action, Move, Shoot, Respond, DoNothing
from core.figures import Figure, IN_MOTION, UNDER_FIRE, NO_EFFECT
from core.game import MISS_MATRIX, hitScoreCalculator
from core.game.board import GameBoard
from core.weapons import Weapon
from utils.coordinates import cube_linedraw
from core.game.pathfinding import reachablePath


class GameManager:
    """
    State of the board of the game.
    """

    def __init__(self, shape: tuple):
        self.shape = shape

        self.name = ""
        self.descr = ""

        # static properties of the board
        self.board = GameBoard(shape)
        self.obstacles = set()

        self.turn = -1

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            RED: [],
            BLUE: []
        }

    # operations on figures (dynamic properties)

    def addFigure(self, agent: str, figure: Figure) -> None:
        """
        Add a figures to the units of the given agent and it setup the index
        in the matrix at the position of the figure.
        """
        figures = self.figures[agent]
        index = len(figures)  # to have 0-based index

        figures.append(figure)
        figure.index = index
        self.board.moveFigure(agent, figure, dst=figure.position)

    def getFigureByIndex(self, agent: str, index: int) -> Figure:
        """Given an index of a figure, return the figure."""
        return self.figures[agent][index]

    def getFiguresByPos(self, agent: str, pos: tuple) -> list:
        """Given a position of a figure, return the figure."""
        return self.board.getFigureByPos(agent, pos)

    # other operations

    def activableFigures(self, agent: str) -> list:
        """Returns a list of figures that have not been activated."""
        # TODO:
        #   transform this in an array that is restored at the beginning of the turn with
        #   the activable figures, when a figure is activated, remove it from such array
        return [f for f in self.figures[agent] if not f.activated and not f.killed]

    def canShoot(self, weapon: Weapon, target: Figure, los: list) -> bool:
        obstacles = [self.board.isObstacle(h) for h in los[1:-2]]

        canHit = weapon.curved or not any(obstacles)  # skip first (who shoots) and last (target) positions
        hasAmmo = weapon.hasAmmo()
        available = weapon.isAvailable()
        isInRange = weapon.max_range >= len(los)

        # TODO: verify that we can use anti-tank against non-vehicles
        if weapon.antitank:
            # can shoot only against vehicles
            validTarget = target.kind == FigureType.VEHICLE
        else:
            # can shoot against infantry and others only
            validTarget = target.kind < FigureType.VEHICLE

        return all([canHit, hasAmmo, available, isInRange, validTarget])

    def buildMovements(self, agent: str, figure: Figure) -> list:
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""

        distance = figure.move - figure.load

        _, movements = reachablePath(figure, self.board, distance)

        return [Move(agent, figure, m) for m in movements]

    def buildShoots(self, agent: str, figure: Figure) -> list:
        """Returns a list of all the possible shooting actions that can be performed."""

        tAgent = RED if agent == BLUE else BLUE
        shoots = []

        for target in self.figures[tAgent]:
            if target.killed:
                continue

            los = cube_linedraw(figure.position, target.position)

            for weapon in figure.weapons:
                if self.canShoot(weapon, target, los):
                    shoots.append(Shoot(agent, figure, target, weapon, los))

        return shoots

    def buildResponses(self, agent: str, figure: Figure) -> list:
        """Returns a list of all possible response action that can be performed."""

        responses = []

        if not figure.responded and not figure.killed and not figure.attackedBy.killed:
            target = figure.attackedBy

            los = cube_linedraw(figure.position, target.position)

            for weapon in figure.weapons:
                if self.canShoot(weapon, target, los):
                    responses.append(Respond(agent, figure, target, weapon, los))

        return responses

    def buildActionForFigure(self, agent: str, figure: Figure) -> list:
        """Build all possible actions for the given figure."""
        actions = []

        for movement in self.buildMovements(agent, figure):
            actions.append(movement)

        for shoot in self.buildShoots(agent, figure):
            actions.append(shoot)

        for response in self.buildResponses(agent, figure):
            actions.append(response)

        return actions

    def buildActions(self, agent: str) -> list:
        """
        Build a list with all the possible actions that can be executed by an agent
        with the current status of the board.
        """
        actions = []

        for figure in self.figures[agent]:
            for action in self.buildActionForFigure(agent, figure):
                actions.append(action)

        return actions

    def activate(self, action: Action) -> dict:
        """Apply the given action to the map."""
        agent = action.agent
        figure = action.figure
        figure.activated = True

        logging.info(action)

        if isinstance(action, DoNothing):
            return {}

        if isinstance(action, Move):
            dest = action.destination[-1]
            self.board.moveFigure(agent, figure, figure.position, dest)
            figure.setSTAT(IN_MOTION)
            return {}

        if isinstance(action, Shoot):  # Respond *is* a shoot action
            f: Figure = figure
            t: Figure = action.target
            w: Weapon = action.weapon
            los: list = action.los

            # TODO: curved weapons (mortar) have different hit computation

            # consume ammunition
            w.shoot()

            score = np.random.choice(range(1, 21), size=w.dices)

            # shoot/response
            if isinstance(action, Respond):
                ATK = w.atk_response
                INT = f.int_def
                # can respond only once in a turn
                f.responded = True
            else:
                ATK = w.atk_normal
                INT = f.int_atk

            # TODO: smoke rule:
            #       if you fire against a panzer, and during the line of sight, you meet a smoke hexagon (not only on
            #       the hexagon where the panzer is), this smoke protection is used, and not the basis one.

            # anti-tank rule
            if w.antitank and t.kind == FigureType.VEHICLE:
                DEF = 0
            else:
                DEF = t.defense_basic

            TER = self.board.getProtectionLevel(t.position)
            STAT = f.stat
            END = f.endurance

            hitScore = hitScoreCalculator(ATK, TER, DEF, STAT, END, INT)

            success = len([x for x in score if x <= hitScore])

            # target status changes for the _next_ hit
            t.setSTAT(UNDER_FIRE)
            # target can now respond to the fire
            t.canRespond(f)

            logging.info(f'{action}: (({success}) {score}/{hitScore})')

            if success > 0:
                t.hp -= success * w.damage
                logging.info(f'{action}: HIT! ({t.hp})')
                t.hit = True
                if t.hp <= 0:
                    t.killed = True
                    logging.info(f'{action}: KILLED!')
                # TODO: choose which weapon to disable
            elif w.curved:
                # mortar
                v = np.random.choice(range(1, 21), size=1)
                hitLocation = MISS_MATRIX[agent](v)
                # TODO: use hit matrix

            else:
                logging.info(f'{action}: miss')

            return {
                'score': score,
                'hitScore': hitScore,
                'ATK': ATK,
                'TER': TER,
                'DEF': DEF,
                'STAT': STAT,
                'END': END,
                'INT': INT,
                'success': success > 0,
                'hits': success,
            }

    def update(self):
        """End turn function that updates the status of all figures and moves forward the internal turn ticker."""
        self.turn += 1

        for agent in [RED, BLUE]:
            for figure in self.figures[agent]:
                figure.update(self.turn)

                # TODO: compute there cutoff status?
                if figure.hp <= 0:
                    figure.killed = True
                    figure.activated = True
                    figure.hit = False
                else:
                    figure.setSTAT(NO_EFFECT)
                    figure.killed = False
                    figure.activated = False
                    figure.responded = False
                    figure.attackedBy = None
                    figure.hit = False

        # TODO: remove killed unit?

    def goalAchieved(self):
        """
        Current is a death match goal.
        """
        redKilled = all([f.killed for f in self.figures[RED]])
        blueKilled = all([f.killed for f in self.figures[BLUE]])

        return redKilled or blueKilled
