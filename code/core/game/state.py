from typing import Dict, List

import numpy as np

from core.actions.basics import ActionFigure
from core.const import RED, BLUE
from core.actions import Action, Attack, AttackGround, LoadInto
from core.figures import Figure, Weapon
from core.game import MAX_SMOKE
from utils.coordinates import to_cube, Cube, cube_linedraw, cube_to_hex


class GameState:
    """
    Dynamic parts of the board.
    """

    __slots__ = [
        'name', 'turn', 'figures', 'posToFigure', 'smoke', 'figuresLOS', 'figuresDistance', 'lastAction',
        'has_choice', 'choices', 'has_placement', 'placement_zone', 'initialized'
    ]

    def __init__(self, shape: tuple, name: str = ''):
        self.name: str = name
        self.turn: int = -1

        # lists of all figures divided by team
        self.figures: Dict[str, List[Figure]] = {
            RED: [],
            BLUE: []
        }

        # contains the figure index at the given position: pos -> [idx, ...]
        self.posToFigure: Dict[str, Dict[Cube, List[int]]] = {
            RED: dict(),
            BLUE: dict(),
        }

        # clouds of smoke on the map
        self.smoke: np.array = np.zeros(shape, dtype='int8')

        # keep track of the line-of-sight to figures (marked by index) of the oppose team
        self.figuresLOS: Dict[str, Dict[int, Dict[int, List[Cube]]]] = {
            RED: dict(),
            BLUE: dict()
        }

        # keep track of the distance by using a line-of-sight between figures (marked by index) of the same team
        self.figuresDistance: Dict[str, Dict[int, Dict[int, List[Cube]]]] = {
            RED: dict(),
            BLUE: dict()
        }

        self.lastAction: Action or None = None

        # group of units that can be chosen
        self.has_choice: Dict[str, bool] = {RED: False, BLUE: False}
        self.choices: Dict[str, Dict[str, List[Figure]]] = {
            RED: dict(),
            BLUE: dict()
        }

        # zones where units can be placed
        self.has_placement: Dict[str, bool] = {RED: False, BLUE: False}
        self.placement_zone: Dict[str, np.ndarray] = {
            RED: np.zeros(shape, dtype='uint8'),
            BLUE: np.zeros(shape, dtype='uint8')
        }

        self.initialized: bool = False

    def vector(self) -> tuple:
        """Convert the state in a vector, used for internal hashing."""
        data = []

        for team in [RED, BLUE]:
            for f in self.figures[team]:
                data += list(f.vector())

        return tuple(data)

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, GameState):
            return False
        v = self.vector()
        v_other = other.vector()
        for i in range(len(v)):
            if v[i] != v_other[i]:
                return False
        return True

    def __hash__(self):
        return hash(self.vector())

    def __repr__(self) -> str:
        return f'GameState({self.name}): {self.turn}:\n{self.figures}\n{self.posToFigure}'

    def completeInit(self):
        """Removes part used for placement of figures."""
        self.has_choice = {RED: False, BLUE: False}
        self.choices = None

        self.has_placement = {RED: False, BLUE: False}
        self.placement_zone = None

        self.initialized = True

    def clearFigures(self, team: str) -> None:
        """Removes all figures from a team."""
        self.figures[team] = []

    def addPlacementZone(self, team: str, zone: np.array):
        """Add a zone in the board where units can be placed."""
        self.has_placement[team] = True
        self.placement_zone[team] += zone

    def addChoice(self, team: str, color: str, *newFigures: Figure) -> None:
        """Add a set of figure to the specified color group of figures."""
        self.has_choice[team] = True
        if color not in self.choices[team]:
            self.choices[team][color] = []
        for figure in newFigures:
            figures = self.choices[team][color]
            figure.index = len(figures)
            figure.color = color
            figures.append(figure)

    def choose(self, team: str, color: str) -> None:
        """Choose and add the figures to use based on the given color."""
        for f in self.choices[team][color]:
            f.color = ''
            self.addFigure(f)

    def addFigure(self, *newFigures: Figure) -> None:
        """
        Add a figures to the units of the given team and set the index in the matrix at the position of the figure.
        """
        for figure in newFigures:
            team = figure.team
            figures = self.figures[team]
            index = len(figures)  # to be 0-based index
            figure.index = index
            figures.append(figure)
            self.moveFigure(figure, dst=figure.position)

    def getFigure(self, action: ActionFigure) -> Figure:
        """Given an action, returns the figure that performs such action."""
        return self.getFigureByIndex(action.team, action.figure_id)

    def getTarget(self, action: Attack) -> Figure:
        """Given an Attack Action, returns the target figure."""
        return self.getFigureByIndex(action.target_team, action.target_id)

    def getWeapon(self, action: Attack or AttackGround) -> Weapon:
        """Given an Attack Action, returns the weapon used."""
        return self.getFigure(action).weapons[action.weapon_id]

    def getTransporter(self, action: LoadInto) -> Figure:
        """Given a LoadInto action, return the destination transporter."""
        return self.getFigureByIndex(action.team, action.transporter_id)

    def getFigures(self, team: str):
        """Returns all figures of a team."""
        return self.figures[team]

    def getFiguresByPos(self, team: str, pos: tuple) -> List[Figure]:
        """Returns all the figures that occupy the given position."""

        # TODO: only one unit per hexagon!

        if len(pos) == 2:
            pos = to_cube(pos)
        if pos not in self.posToFigure[team]:
            return []
        return [self.getFigureByIndex(team, i) for i in self.posToFigure[team][pos]]

    def getFigureByIndex(self, team: str, index: int) -> Figure:
        """Given an index of a figure, return the figure."""
        return self.figures[team][index]

    def getFiguresCanBeActivated(self, team: str) -> List[Figure]:
        """Returns a list of figures that have not been activated."""
        return [f for f in self.figures[team] if not f.activated and not f.killed]

    def getFiguresCanRespond(self, team: str) -> List[Figure]:
        """Returns a list of figures that have not responded."""
        return [f for f in self.figures[team] if not f.responded and not f.killed]

    def getMovementCost(self, pos: Cube) -> float:
        figures = self.getFiguresByPos(RED, pos) + self.getFiguresByPos(BLUE, pos)
        for figure in figures:
            if not figure.killed:
                return 1000.0
        return 0.0

    def moveFigure(self, figure: Figure, curr: Cube = None, dst: Cube = None) -> None:
        """Moves a figure from current position to another destination."""
        ptf = self.posToFigure[figure.team]
        if curr:
            ptf[curr].remove(figure.index)
            if len(ptf[curr]) == 0:
                ptf.pop(curr, None)
        if dst:
            if dst not in ptf:
                ptf[dst] = list()
            ptf[dst].append(figure.index)
            figure.goto(dst)
            self.updateLOS(figure)

    def getLOS(self, target: Figure) -> Dict[int, List[Cube]]:
        """Get all the lines of sight of all hostile figures of the given target."""
        return self.figuresLOS[target.team][target.index]

    def getDistance(self, target: Figure) -> Dict[int, List[Cube]]:
        """Get all the lines of sight of all ally figures of the given target."""
        return self.figuresDistance[target.team][target.index]

    def updateLOS(self, target: Figure) -> None:
        """Updates all the lines of sight for the current target."""
        defenders = target.team
        attackers = RED if defenders == BLUE else BLUE

        for attacker in self.figures[attackers]:
            if target.index not in self.figuresLOS[defenders]:
                self.figuresLOS[defenders][target.index] = {}
            if attacker.index not in self.figuresLOS[attackers]:
                self.figuresLOS[attackers][attacker.index] = {}

            self.figuresLOS[attackers][attacker.index][target.index] = cube_linedraw(target.position, attacker.position)
            self.figuresLOS[defenders][target.index][attacker.index] = cube_linedraw(attacker.position, target.position)

        self.figuresDistance[defenders][target.index] = {
            # defender's line of sight
            defender.index: cube_linedraw(defender.position, target.position)
            for defender in self.figures[defenders]
        }

    def isObstacle(self, pos: Cube) -> bool:
        """Returns if the position is an obstacle (a VEHICLE) to LOS or not."""
        for team in (RED, BLUE):
            for f in self.getFiguresByPos(team, pos):
                if f.kind == 'vehicle':
                    return True
        return False

    def addSmoke(self, smoke: list) -> None:
        """Add a cloud of smoke to the status. This cloud is defined by a list of Cubes."""
        for h in smoke:
            self.smoke[cube_to_hex(h)] = MAX_SMOKE

    def hasSmoke(self, lof: list) -> bool:
        """
        Smoke rule: if you fire against a panzer, and during the line of sight, you meet a smoke hexagon (not only on
        the hexagon where the panzer is), this smoke protection is used, and not the basic protection value.
        """
        return any([self.smoke[cube_to_hex(h)] > 0 for h in lof])

    def reduceSmoke(self) -> None:
        """Reduce by 1 the counter for of smoke clouds."""
        self.smoke = np.clip(self.smoke - 1, 0, MAX_SMOKE)
