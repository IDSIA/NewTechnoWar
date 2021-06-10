import math
from os import W_OK
import os.path as op
from typing import List, Tuple

from PIL import Image, ImageColor, ImageDraw
from numpy import isin

from core.const import RED, BLUE
from core.game import GameBoard, GameState, TYPE_TERRAIN
from core.actions import Action, Move, Attack
from core.scenarios.functions import parseBoard, buildScenario
from core.utils.coordinates import Hex

SIZE: int = 18
ALWAYS_ACTIONS: bool = False
SQRT3: float = math.sqrt(3)

IMAGE_FOLDER: str = op.join(op.dirname(__file__), '..', 'images')
PATH_INF: str = op.join(IMAGE_FOLDER, 'infantry.png')
PATH_TANK: str = op.join(IMAGE_FOLDER, 'tank.png')

COLORS: dict = {
    RED: '#ff0000',
    BLUE: '#1e90ff',
}


def _evenqOffsetToPixel(i: int = 0, j: int = 0, size=SIZE, pos: tuple = None) -> Tuple[int, int]:
    if pos:
        i, j = pos
    x = size * 3 / 2 * i
    y = size * SQRT3 * (j - 0.5 * (i & 1))
    return int(x + size), int(y + size * 2)


def _hexagonPoints(i: int = 0, j: int = 0, size=SIZE, pos: tuple = None) -> List:
    if pos:
        i, j = pos
    w = size / 2
    h = round(size * SQRT3 / 2)
    return [
        (i + w, j + -h),
        (i + -w, j + -h),
        (i + -2 * w, j + 0),
        (i + -w, j + h),
        (i + w, j + h),
        (i + 2 * w, j + 0),
        (i + w, j + -h),
    ]


def _drawHexagon(img: Image, i: int, j: int, size=SIZE, color: str = 'white', alpha: int = 255) -> None:
    draw = ImageDraw.Draw(img, 'RGBA')
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.polygon(points, fill=(r, g, b, alpha), outline=None)


def _drawHexagonBorder(img: Image, i: int, j: int, size, color: str = 'white', width: int = 1) -> None:
    width = int(max(1, size * width * .09))

    draw = ImageDraw.Draw(img, 'RGBA')
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.line(points, fill=(r, g, b), width=width)


def drawBoard(board: GameBoard, size=SIZE) -> Image:
    x, y = board.shape
    size_x = x * 2 * size
    size_y = y * 2 * size

    img = Image.new('RGB', (size_x, size_y), 'white')

    maxi, maxj = 0, 0

    for i in range(0, x):
        for j in range(0, y):
            index = board.terrain[i, j]
            tt = TYPE_TERRAIN[index]

            pi, pj = _evenqOffsetToPixel(i, j, size)
            _drawHexagon(img, pi, pj, size, color=tt.color)
            _drawHexagonBorder(img, pi, pj, size, 'black')
            maxi = max(maxi, pi)
            maxj = max(maxj, pj)

    for mark in board.getObjectiveMark():
        a, b = mark.tuple()
        pi, pj = _evenqOffsetToPixel(a, b, size)
        _drawHexagonBorder(img, pi, pj, size - 1, 'yellow', 2)

    return img.crop((0, 0, maxi + size, maxj + size))


def board2png(filename: str, boardName: str, format: str = 'PNG', size=SIZE) -> None:
    if op.exists(filename):
        return

    board = parseBoard(boardName)
    img = drawBoard(board, size)
    img.save(filename, format)


def drawState(board: GameBoard, state: GameState, last_action: bool = ALWAYS_ACTIONS, size=SIZE) -> Image:
    img: Image = drawBoard(board, size)

    x, y = board.shape

    psize = int(size * .6)

    img_inf: Image = Image.open(PATH_INF)
    img_tank: Image = Image.open(PATH_TANK)

    psize2 = 2 * psize

    img_inf.thumbnail((psize2, psize2), Image.ANTIALIAS)
    img_tank.thumbnail((psize2, psize2), Image.ANTIALIAS)

    decals = {
        'vehicle': img_tank,
        'infantry': img_inf,
    }

    if last_action and state.lastAction:
        drawAction(img, state.lastAction, size=size)

    for i in range(0, x):
        for j in range(0, y):

            pos = Hex(i, j).cube()
            pi, pj = _evenqOffsetToPixel(i, j, size)

            for team in [RED, BLUE]:
                if state.has_placement[RED] and state.placement_zone[RED][i, j] > 0:
                    _drawHexagon(img, pi, pj, size, color=COLORS[team], alpha=64)

                fs = state.getFiguresByPos(team, pos)
                for f in fs:
                    _drawFigure(img, pi, pj, psize, f, decals)

    return img


def _drawFigure(img: Image, pi, pj, psize, figure, decals) -> None:
    xy = (pi - psize, pj - psize, pi + psize, pj + psize)
    dxy = (pi - psize, pj - psize)

    draw = ImageDraw.Draw(img, 'RGBA')
    draw.ellipse(xy, fill=COLORS[figure.team])

    if figure.killed:
        psize = psize * .81
        xy = (pi - psize, pj - psize, pi + psize, pj + psize)
        draw.ellipse(xy, fill='#555555')

    decal = decals[figure.kind]
    img.paste(decal, dxy, mask=decal)


def drawAction(img: Image, action: Action, size=SIZE) -> None:

    w = int(max(1, size * .3))

    draw = ImageDraw.Draw(img, 'RGBA')

    if isinstance(action, Move):
        path = [_evenqOffsetToPixel(pos=p.tuple(), size=size) for p in action.path]
        draw.line(path, fill=(255, 255, 255, 176), width=w)

    if isinstance(action, Attack):
        lof = [_evenqOffsetToPixel(pos=p.tuple(), size=size) for p in action.lof]
        los = [_evenqOffsetToPixel(pos=p.tuple(), size=size) for p in action.los]

        rgb_los = (255, 0, 0, 128) if action.team == RED else (0, 0, 255, 128)
        rgb_lof = (255, 0, 0, 255) if action.team == RED else (0, 0, 255, 255)

        draw.line(los, fill=rgb_los, width=w)
        draw.line(lof, fill=rgb_lof, width=w)


def scenario2png(filename: str, scenario, format: str = 'PNG', size=SIZE) -> None:
    if op.exists(filename):
        return

    board, state = buildScenario(scenario)
    img = drawState(board, state, size=size)
    img.save(filename, format)
