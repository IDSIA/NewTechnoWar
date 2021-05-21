import math
import os

from PIL import Image, ImageColor, ImageDraw

from core.const import RED, BLUE
from core.scenarios.functions import parseBoard, buildScenario
from web.server.utils import scroll

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


def drawBoard(board, size=10):
    x, y = board.shape
    x *= 2 * size
    y *= 2 * size

    img = Image.new('RGB', (x, y), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    maxi, maxj = 0, 0

    for hex in scroll(board):
        i, j = _evenqOffsetToPixel(hex.i, hex.j, size)
        _drawHexagon(draw, i, j, size, color=hex.color)
        _drawHexagonBorder(draw, i, j, size, 'black')
        maxi = max(maxi, i)
        maxj = max(maxj, j)

    for mark in board.getObjectiveMark():
        a, b = mark.tuple()
        i, j = _evenqOffsetToPixel(a, b, size)
        _drawHexagonBorder(draw, i, j, size - 1, 'yellow', 2)

    return img.crop((0, 0, maxi + 14, maxj + 20))


def board2png(filename: str, boardName: str, format: str = 'PNG', size=10) -> None:
    if os.path.exists(filename):
        return

    board = parseBoard(boardName)
    img = drawBoard(board, size)
    img.save(filename, format)


def drawState(board, state, size=10):
    img = drawBoard(board, size)
    draw = ImageDraw.Draw(img, 'RGBA')

    psize = size * .6

    for hex in scroll(board):
        i, j = _evenqOffsetToPixel(hex.i, hex.j, size)

        if state.has_placement[RED] and state.placement_zone[RED][hex.i, hex.j] > 0:
            _drawHexagon(draw, i, j, size, color='#ff0000', alpha=64)
        if state.has_placement[BLUE] and state.placement_zone[BLUE][hex.i, hex.j] > 0:
            _drawHexagon(draw, i, j, size, color='#1e90ff', alpha=64)

        fs = state.getFiguresByPos(RED, hex.cube)
        xy = (i - psize, j - psize, i + psize, j + psize)
        for f in fs:
            if f.kind == 'vehicle':
                draw.ellipse(xy, fill='#ff0000')
            else:
                draw.ellipse(xy, outline='#ff0000', width=2)

        fs = state.getFiguresByPos(BLUE, hex.cube)
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
