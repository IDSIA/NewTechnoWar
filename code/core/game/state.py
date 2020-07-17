import numpy as np

from core import RED, BLUE
from core.figures import FigureType, Figure
from utils.coordinates import to_cube, Cube, cube_linedraw


class GameState:
    """
    Dynamic parts of the board.
    """

    __slots__ = ['turn', 'figures', 'posToFigure', 'smoke', 'figuresLos']

    def __init__(self, shape: tuple):
        self.turn = -1

        # list of all figures
        self.figures = {
            RED: [],
            BLUE: []
        }

        # contains the figure index at the given position: pos -> [idx, ...]
        self.posToFigure = {
            RED: dict(),
            BLUE: dict(),
        }

        self.smoke = np.zeros(shape, dtype='uint8')

        self.figuresLos = {
            RED: dict(),
            BLUE: dict()
        }

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

    def getLos(self, target: Figure) -> dict:
        return self.figuresLos[target.agent][target.index]

    def updateLos(self, target: Figure) -> None:
        attackers = RED if target.agent == BLUE else BLUE

        self.figuresLos[target.agent][target.index] = {
            # attacker's line of sight
            attacker.index: cube_linedraw(attacker.position, target.position)
            for attacker in self.figures[attackers]
        }

    def addSmoke(self, area: np.array) -> None:
        self.smoke += area

    def getFigureByPos(self, agent: str, pos: tuple) -> list:
        """Returns all the figures that occupy the given position."""
        if len(pos) == 2:
            pos = to_cube(pos)
        if pos not in self.posToFigure[agent]:
            return []
        return self.posToFigure[agent][pos]

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

    def isObstacle(self, pos: Cube) -> bool:
        """Returns if the position is an obstacle (a VEHICLE) to LOS or not."""
        for agent in (RED, BLUE):
            for f in self.getFigureByPos(agent, pos):
                if f.kind == FigureType.VEHICLE:
                    return True
        return False

    def activableFigures(self, agent: str) -> list:
        """Returns a list of figures that have not been activated."""
        # TODO:
        #   transform this in an array that is restored at the beginning of the turn with
        #   the activable figures, when a figure is activated, remove it from such array
        return [f for f in self.figures[agent] if not f.activated and not f.killed]
