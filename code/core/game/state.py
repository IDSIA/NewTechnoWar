import numpy as np

from core import RED, BLUE
from core.figures import FigureType, Figure
from utils.coordinates import to_cube, Cube


class GameState:
    """
    Dynamic parts of the board.
    """

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

        # TODO:

    def __repr__(self):
        return f'{self.turn}:\n{self.figures}\n{self.posToFigure}'

    def addFigure(self, agent: str, figure: Figure) -> None:
        """
        Add a figures to the units of the given agent and it setup the index
        in the matrix at the position of the figure.
        """
        figures = self.figures[agent]
        index = len(figures)  # to have 0-based index
        figures.append(figure)
        figure.index = index
        self.moveFigure(agent, figure, dst=figure.position)

    def addSmoke(self, area: np.array):
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
