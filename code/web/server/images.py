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
    return x, y


def _drawHexagon(draw, i, j, color, alpha=255, size=10):
    i, j = _evenqOffsetToPixel(i, j, size)
    i += 14
    j += 20

    r, g, b = ImageColor.getrgb(color)

    draw.polygon([
        (i + 5, j + -9),
        (i + -5, j + -9),
        (i + -10, j + 0),
        (i + -5, j + 9),
        (i + 5, j + 9),
        (i + 10, j + 0)
    ], fill=(r, g, b, alpha), outline='black')
    return i, j


def board2png(filename: str, boardName: str, format: str = 'PNG') -> None:
    if os.path.exists(filename):
        return

    board = parseBoard(boardName)

    x, y = board.shape
    x *= 20
    y *= 20

    img = Image.new('RGB', (x, y), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    maxi, maxj = 0, 0

    for hex in scroll(board):
        i, j = _drawHexagon(draw, hex.i, hex.j, hex.color)
        maxi = max(maxi, i)
        maxj = max(maxj, j)

    img = img.crop((0, 0, maxi + 14, maxj + 14))

    img.save(filename, format)


def scenario2png(filename: str, scenario, format: str = 'PNG') -> None:
    if os.path.exists(filename):
        return

    board, state = buildScenario(scenario)

    psize = 6

    x, y = board.shape
    x *= 20
    y *= 20

    img = Image.new('RGB', (x, y), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    maxi, maxj = 0, 0

    for hex in scroll(board):
        i, j = _drawHexagon(draw, hex.i, hex.j, hex.color)

        _drawHexagon(draw, hex.i, hex.j, hex.color)

        if state.placement_zone[RED][hex.i, hex.j] > 0:
            _drawHexagon(draw, hex.i, hex.j, '#ff0000', 64)
        if state.placement_zone[BLUE][hex.i, hex.j] > 0:
            _drawHexagon(draw, hex.i, hex.j, '#1e90ff', 64)

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

        maxi = max(maxi, i)
        maxj = max(maxj, j)

    img = img.crop((0, 0, maxi + 14, maxj + 14))

    img.save(filename, format)
