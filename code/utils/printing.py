from numpy import np

from core import RED, BLUE, FigureType
from core.game import GameManager
from utils.colors import yellow, green, red, blue, pinkBg, grayBg


def printState(gm: GameManager, size=3, extra: list = None):
    cols, rows = gm.shape

    board_extra = np.zeros(gm.shape, dtype='uint8')

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

            if gm.board.objective[p] > 0:
                cell[1] = yellow('x')

            if board_extra[p] > 0:
                cell[0] = green('x')

            redFigure = gm.board.figures[RED][p]
            if redFigure > 0:
                figure = gm.getFigureByPos(RED, (c, r))

                cell[1] = red('T') if figure.kind == FigureType.VEHICLE else red('I')

            blueFigure = gm.board.figures[BLUE][p]
            if blueFigure > 0:
                figure = gm.getFigureByPos(BLUE, (c, r))

                cell[1] = blue('T') if figure.kind == FigureType.VEHICLE else blue('I')

            if gm.board.obstacles[p] > 0:
                cell = [pinkBg(c) for c in cell]
            if gm.board.roads[p] > 0:
                cell = [grayBg(c) for c in cell]

            line.append(''.join(cell))

        print('|' + '|'.join([l for l in line] + [f' {r}']))
    print('+' + sep_horizontal + '+')
