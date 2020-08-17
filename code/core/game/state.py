import numpy as np

from core import RED, BLUE
from core.actions import Action, Attack, AttackGround, LoadInto
from core.figures import FigureType, Figure, Weapon
from core.game import MAX_SMOKE
from utils.coordinates import to_cube, Cube, cube_linedraw, cube_to_hex


class GameState:
    """
    Dynamic parts of the board.
    """

    __slots__ = ['name', 'turn', 'figures', 'posToFigure', 'smoke', 'figuresLOS', 'figuresDistance', 'lastAction']

    def __init__(self, shape: tuple, name: str = ''):
        self.name: str = name
        self.turn: int = -1

        # lists of all figures divided by team
        self.figures: dict = {
            RED: [],
            BLUE: []
        }

        # contains the figure index at the given position: pos -> [idx, ...]
        self.posToFigure: dict = {
            RED: dict(),
            BLUE: dict(),
        }

        # clouds of smoke on the map
        self.smoke: np.array = np.zeros(shape, dtype='int8')

        # keep track of the line-of-sight to figures (marked by index) of the oppose team
        self.figuresLOS: dict = {
            RED: dict(),
            BLUE: dict()
        }

        # keep track of the distance by using a line-of-sight between figures (marked by index) of the same team
        self.figuresDistance: dict = {
            RED: dict(),
            BLUE: dict()
        }

        self.lastAction: Action or None = None

    def __repr__(self) -> str:
        return f'{self.turn}:\n{self.figures}\n{self.posToFigure}'

    def addFigure(self, figure: Figure) -> None:
        """
        Add a figures to the units of the given agent and it setup the index
        in the matrix at the position of the figure.
        """
        team = figure.team
        figures = self.figures[team]
        index = len(figures)  # to have 0-based index
        figures.append(figure)
        figure.index = index
        self.moveFigure(team, figure, dst=figure.position)

    def getFigure(self, action: Action) -> Figure:
        """Given an action, returns the figure that performs such action."""
        return self.getFigureByIndex(action.team, action.fid)

    def getTarget(self, action: Attack) -> Figure:
        """Given an Attack Action, returns the target figure."""
        return self.getFigureByIndex(action.target_team, action.target_id)

    def getWeapon(self, action: Attack or AttackGround) -> Weapon:
        """Given an Attack Action, returns the weapon used."""
        return self.getFigure(action).weapons[action.weapon_id]

    def getTransporter(self, action: LoadInto) -> Figure:
        """Given a LoadInto action, return the destination transporter."""
        return self.getFigureByIndex(action.team, action.transporter_id)

    def getFiguresByPos(self, team: str, pos: tuple) -> list:
        """Returns all the figures that occupy the given position."""
        if len(pos) == 2:
            pos = to_cube(pos)
        if pos not in self.posToFigure[team]:
            return []
        return [self.getFigureByIndex(team, i) for i in self.posToFigure[team][pos]]

    def getFigureByIndex(self, team: str, index: int) -> Figure:
        """Given an index of a figure, return the figure."""
        return self.figures[team][index]

    def getFiguresCanBeActivated(self, team: str) -> list:
        """Returns a list of figures that have not been activated."""
        return [f for f in self.figures[team] if not f.activated and not f.killed]

    def getFiguresCanRespond(self, team: str) -> list:
        """Returns a list of figures that have not responded."""
        return [f for f in self.figures[team] if not f.responded and not f.killed]

    def moveFigure(self, team: str, figure: Figure, curr: Cube = None, dst: Cube = None) -> None:
        """Moves a figure from current position to another destination."""
        ptf = self.posToFigure[team]
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

    def getLOS(self, target: Figure) -> dict:
        """Get all the lines of sight of all hostile figures of the given target."""
        return self.figuresLOS[target.team][target.index]

    def getDistance(self, target: Figure) -> dict:
        """Get all the lines of sight of all ally figures of the given target."""
        return self.figuresDistance[target.team][target.index]

    def updateLOS(self, target: Figure) -> None:
        """Updates all the lines of sight for the current target."""
        defenders = target.team
        attackers = RED if defenders == BLUE else BLUE

        self.figuresLOS[defenders][target.index] = {
            # attacker's line of sight
            attacker.index: cube_linedraw(attacker.position, target.position)
            for attacker in self.figures[attackers]
        }

        self.figuresDistance[defenders][target.index] = {
            # defender's line of sight
            defender.index: cube_linedraw(defender.position, target.position)
            for defender in self.figures[defenders]
        }

    def isObstacle(self, pos: Cube) -> bool:
        """Returns if the position is an obstacle (a VEHICLE) to LOS or not."""
        for agent in (RED, BLUE):
            for f in self.getFiguresByPos(agent, pos):
                if f.kind == FigureType.VEHICLE:
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
