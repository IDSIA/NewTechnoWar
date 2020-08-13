import numpy as np

from core import RED, BLUE
from core.actions import Action
from core.figures import FigureType, Figure
from utils.coordinates import to_cube, Cube, cube_linedraw, cube_to_hex


class GameState:
    """
    Dynamic parts of the board.
    """

    __slots__ = ['name', 'turn', 'figures', 'posToFigure', 'smoke', 'figuresLos', 'lastAction']

    def __init__(self, shape: tuple, name: str = ''):
        self.name: str = name
        self.turn: int = -1

        # list of all figures
        self.figures: dict = {
            RED: [],
            BLUE: []
        }

        # contains the figure index at the given position: pos -> [idx, ...]
        self.posToFigure: dict = {
            RED: dict(),
            BLUE: dict(),
        }

        self.smoke: np.array = np.zeros(shape, dtype='uint8')

        self.figuresLos: dict = {
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
        agent = figure.agent
        figures = self.figures[agent]
        index = len(figures)  # to have 0-based index
        figures.append(figure)
        figure.index = index
        self.moveFigure(agent, figure, dst=figure.position)

    def getFigureByPos(self, agent: str, pos: tuple) -> list:
        """Returns all the figures that occupy the given position."""
        if len(pos) == 2:
            pos = to_cube(pos)
        if pos not in self.posToFigure[agent]:
            return []
        return self.posToFigure[agent][pos]

    def getFigureByIndex(self, agent: str, index: int) -> Figure:
        """Given an index of a figure, return the figure."""
        return self.figures[agent][index]

    def getFiguresActivatable(self, agent: str) -> list:
        """Returns a list of figures that have not been activated."""
        return [f for f in self.figures[agent] if not f.activated and not f.killed]

    def getFiguresRespondatable(self, agent: str) -> list:
        """Returns a list of figures that have not responded."""
        return [f for f in self.figures[agent] if not f.responded and not f.killed]

    def moveFigure(self, agent: str, figure: Figure, curr: Cube = None, dst: Cube = None) -> None:
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
            self.updateLos(figure)

    def getLos(self, target: Figure) -> dict:
        return self.figuresLos[target.agent][target.index]

    def updateLos(self, target: Figure) -> None:
        attackers = RED if target.agent == BLUE else BLUE

        self.figuresLos[target.agent][target.index] = {
            # attacker's line of sight
            attacker.index: cube_linedraw(attacker.position, target.position)
            for attacker in self.figures[attackers]
        }

    def isObstacle(self, pos: Cube) -> bool:
        """Returns if the position is an obstacle (a VEHICLE) to LOS or not."""
        for agent in (RED, BLUE):
            for f in self.getFigureByPos(agent, pos):
                if f.kind == FigureType.VEHICLE:
                    return True
        return False

    def addSmoke(self, area: np.array) -> None:
        self.smoke += area

    def hasSmoke(self, lof: list) -> bool:
        """
        Smoke rule: if you fire against a panzer, and during the line of sight, you meet a smoke hexagon (not only on
        the hexagon where the panzer is), this smoke protection is used, and not the basic protection value.
        """
        return any([self.smoke[cube_to_hex(h)] > 0 for h in lof])
