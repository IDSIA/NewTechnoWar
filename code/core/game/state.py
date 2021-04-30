from typing import Dict, List

import numpy as np

from core.actions import Action, Attack, AttackGround
from core.actions import ActionFigure, MoveLoadInto
from core.const import RED, BLUE
from core.figures import Figure, Weapon
from core.figures.figure import vectorFigureInfo
from core.game.static import MAX_UNITS_PER_TEAM, MAX_SMOKE
from core.utils.coordinates import Cube


class GameState:
    """
    Dynamic parts of the board.
    """

    __slots__ = [
        'name', 'seed', 'turn', 'figures', 'posToFigure', 'smoke', 'figuresLOS', 'figuresDistance', 'lastAction',
        'has_choice', 'choices', 'has_placement', 'placement_zone', 'initialized'
    ]

    def __init__(self, shape: tuple, name: str = '', seed=0):
        self.name: str = name
        self.seed: int = seed
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

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, GameState):
            return False
        v = vectorState(self)
        v_other = vectorState(other)
        for i in range(len(v)):
            if v[i] != v_other[i]:
                return False
        return True

    def __hash__(self):
        return hash(vectorState(self))

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

    def getTransporter(self, action: MoveLoadInto) -> Figure:
        """Given a LoadInto action, return the destination transporter."""
        return self.getFigureByIndex(action.team, action.transporter_id)

    def getFigures(self, team: str):
        """Returns all figures of a team."""
        return self.figures[team]

    def getFiguresByPos(self, team: str, pos: Cube) -> List[Figure]:
        """Returns all the figures that occupy the given position."""

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

    def getMovementCost(self, pos: Cube, kind: str) -> float:
        # TODO: this method is for future expansions
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

    def getDistances(self, target: Figure) -> Dict[int, List[Cube]]:
        """Get all the lines of sight of all ally figures of the given target."""
        return self.figuresDistance[target.team][target.index]

    def updateLOS(self, target: Figure) -> None:
        """Updates all the lines of sight for the current target."""
        defenders = target.team
        attackers = RED if defenders == BLUE else BLUE

        for attacker in self.figures[attackers]:
            los = target.position.line(attacker.position)

            self.figuresLOS[defenders].setdefault(target.index, {})[attacker.index] = los
            self.figuresLOS[attackers].setdefault(attacker.index, {})[target.index] = list(reversed(los))

        for defender in self.figures[defenders]:
            los = target.position.line(defender.position)

            self.figuresDistance[defenders].setdefault(target.index, {})[defender.index] = los
            self.figuresDistance[defenders].setdefault(defender.index, {})[target.index] = list(reversed(los))

    def isObstacle(self, pos: Cube) -> bool:
        """Returns if the position is an obstacle (a VEHICLE) to LOS or not."""
        for team in (RED, BLUE):
            for f in self.getFiguresByPos(team, pos):
                if f.kind == 'vehicle':
                    return True
        return False

    def addSmoke(self, smoke: List[Cube]) -> None:
        """Add a cloud of smoke to the status. This cloud is defined by a list of Cubes."""
        for c in smoke:
            self.smoke[c.tuple()] = MAX_SMOKE

    def hasSmoke(self, lof: List[Cube]) -> bool:
        """
        Smoke rule: if you fire against a panzer, and during the line of sight, you meet a smoke hexagon (not only on
        the hexagon where the panzer is), this smoke protection is used, and not the basic protection value.
        """
        return any([self.smoke[c.tuple()] > 0 for c in lof])

    def reduceSmoke(self) -> None:
        """Reduce by 1 the counter for of smoke clouds."""
        self.smoke = np.clip(self.smoke - 1, 0, MAX_SMOKE)


def vectorStateInfo() -> tuple:
    """Convert the state in a vector, used for internal hashing."""
    info = [
        "meta_seed", "meta_scenario", "turn"
    ]

    for team in [RED, BLUE]:
        for i in range(MAX_UNITS_PER_TEAM):
            meta = f'{team}_figure_{i}'
            info += vectorFigureInfo(meta)

    # distance between figures of same team
    for team in [RED, BLUE]:
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                if i != j:
                    info.append(f'{team}_distance_{i}_{j}')

    # LOS between figures of different team
    for team in [RED, BLUE]:
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                info.append(f'{team}_LOS_{i}_{j}')

    return tuple(info)


def vectorState(state: GameState) -> tuple:
    """Convert the state in a vector, used for internal hashing."""
    data = [
        state.seed,
        state.name,
        state.turn,
    ]

    x: int = len(vectorFigureInfo(''))

    for team in [RED, BLUE]:
        for i in range(MAX_UNITS_PER_TEAM):
            if i < len(state.figures[team]):
                f: Figure = state.figures[team][i]
                data += list(f.vector())
            else:
                data += [None] * x

    for teams in [(RED, BLUE), (BLUE, RED)]:
        team, other = teams
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                if i != j:
                    if i < len(state.figures[team]) and j < len(state.figures[team]):
                        dist: list = state.figuresDistance[team][j][i]
                        data.append(len(dist) - 1)
                    else:
                        data.append(None)

    for teams in [(RED, BLUE), (BLUE, RED)]:
        team, other = teams
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                if i < len(state.figures[team]) and j < len(state.figures[other]):
                    dist: list = state.figuresLOS[team][i][j]
                    data.append(len(dist) - 1)
                else:
                    data.append(None)

    return tuple(data)
