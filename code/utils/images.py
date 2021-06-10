import math
import os

from PIL import Image, ImageColor, ImageDraw

from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import TYPE_TERRAIN
from core.scenarios.functions import parseBoard, buildScenario
from core.utils.coordinates import Hex


sqrt3 = math.sqrt(3)


def _evenqOffsetToPixel(i: int, j: int, size):
    x = size * 3 / 2 * i
    y = size * sqrt3 * (j - 0.5 * (i & 1))
    return int(x + size), int(y + size * 2)


def _hexagonPoints(i, j, size):
    w = size / 2
    h = round(size * sqrt3 / 2)
    return [
        (i + w, j + -h),
        (i + -w, j + -h),
        (i + -2 * w, j + 0),
        (i + -w, j + h),
        (i + w, j + h),
        (i + 2 * w, j + 0),
        (i + w, j + -h),
    ]


def _drawHexagon(draw, i, j, size, color='white', alpha=255):
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.polygon(points, fill=(r, g, b, alpha), outline=None)


def _drawHexagonBorder(draw, i, j, size, color='white', width=1):
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.line(points, fill=(r, g, b), width=width)


def drawBoard(board: GameBoard, size=10):
    x, y = board.shape
    size_x = x * 2 * size
    size_y = y * 2 * size

    img = Image.new('RGB', (size_x, size_y), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    maxi, maxj = 0, 0

    for i in range(0, x):
        for j in range(0, y):
            index = board.terrain[i, j]
            tt = TYPE_TERRAIN[index]

            pi, pj = _evenqOffsetToPixel(i, j, size)
            _drawHexagon(draw, pi, pj, size, color=tt.color)
            _drawHexagonBorder(draw, pi, pj, size, 'black')
            maxi = max(maxi, pi)
            maxj = max(maxj, pj)

    for mark in board.getObjectiveMark():
        a, b = mark.tuple()
        pi, pj = _evenqOffsetToPixel(a, b, size)
        _drawHexagonBorder(draw, pi, pj, size - 1, 'yellow', 2)

    return img.crop((0, 0, maxi + 14, maxj + 20))


def board2png(filename: str, boardName: str, format: str = 'PNG', size=10) -> None:
    if os.path.exists(filename):
        return

    board = parseBoard(boardName)
    img = drawBoard(board, size)
    img.save(filename, format)


def drawState(board: GameBoard, state: GameState, size=10):
    img = drawBoard(board, size)
    draw = ImageDraw.Draw(img, 'RGBA')

    x, y = board.shape

    psize = size * .6

    for i in range(0, x):
        for j in range(0, y):

            pos = Hex(i, j).cube()
            pi, pj = _evenqOffsetToPixel(i, j, size)

            if state.has_placement[RED] and state.placement_zone[RED][i, j] > 0:
                _drawHexagon(draw, pi, pj, size, color='#ff0000', alpha=64)
            if state.has_placement[BLUE] and state.placement_zone[BLUE][i, j] > 0:
                _drawHexagon(draw, pi, pj, size, color='#1e90ff', alpha=64)

            fs = state.getFiguresByPos(RED, pos)
            xy = (pi - psize, pj - psize, pi + psize, pj + psize)
            for f in fs:
                if f.kind == 'vehicle':
                    draw.ellipse(xy, fill='#ff0000')
                else:
                    draw.ellipse(xy, outline='#ff0000', width=2)

            fs = state.getFiguresByPos(BLUE, pos)
            for f in fs:
                if f.kind == 'vehicle':
                    draw.ellipse(xy, fill='#1e90ff')
                else:
                    draw.ellipse(xy, outline='#1e90ff', width=2)

    return img


def scenario2png(filename: str, scenario, format: str = 'PNG', size=10) -> None:
    if os.path.exists(filename):
        return

    board, state = buildScenario(scenario)
    img = drawState(board, state, size)
    img.save(filename, format)
