from numpy import np
from core.state import StateOfTheBoard
from core.figures import FigureType
from core import RED, BLUE
from utils.colors import yellow, green, red, blue, pinkBg, grayBg


def print(state: StateOfTheBoard, size=3, extra: list = None):
    cols, rows = state.shape

    board_extra = np.zeros(state.shape, dtype='uint8')

    if extra:
        for e in extra:
            board_extra[e] = 1

    sep_horizontal = '+'.join(['-' * size] * cols)

    print('+' + '|'.join([f' {c} ' for c in range(0, rows)]), '+')
    print('+' + sep_horizontal + '+')

    for r in range(rows):
        line = []
        for c in range(cols):
            p = (c, r)
            cell = [' '] * size

            if state.board.objective[p] > 0:
                cell[1] = yellow('x')

            if board_extra[p] > 0:
                cell[0] = green('x')

            redFigure = state.board.figures[RED][p]
            if redFigure > 0:
                figure = state.getFigureByPos(RED, (c, r))

                cell[1] = red('T') if figure.kind == FigureType.VEHICLE else red('I')

            blueFigure = state.board.figures[BLUE][p]
            if blueFigure > 0:
                figure = state.getFigureByPos(BLUE, (c, r))

                cell[1] = blue('T') if figure.kind == FigureType.VEHICLE else blue('I')

            if state.board.obstacles[p] > 0:
                cell = [pinkBg(c) for c in cell]
            if state.board.roads[p] > 0:
                cell = [grayBg(c) for c in cell]

            line.append(''.join(cell))

        print('|' + '|'.join([l for l in line] + [f' {r}']))
    print('+' + sep_horizontal + '+')
