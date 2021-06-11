import math
import os.path as op

from typing import Dict, List, Tuple

from PIL import Image, ImageColor, ImageDraw
from numpy import isin

from core.const import RED, BLUE
from core.game import GameBoard, GameState, TYPE_TERRAIN
from core.figures import stat
from core.actions import Action, Move, Attack
from core.scenarios.functions import parseBoard, buildScenario
from core.utils.coordinates import Hex

SIZE: int = 18
ALWAYS_ACTIONS: bool = False
SQRT3: float = math.sqrt(3)

IMAGE_FOLDER: str = op.join(op.dirname(__file__), '..', 'images')
IMAGE_DECALS: dict = {
    'infantry':  op.join(IMAGE_FOLDER, 'infantry.png'),
    'vehicle': op.join(IMAGE_FOLDER, 'tank.png'),
    'hidden': op.join(IMAGE_FOLDER, 'hidden.png'),
}

COLORS: dict = {
    RED: '#ff0000',
    BLUE: '#1e90ff',
}


def _loadDecals(psize: int) -> Dict[str, Image.Image]:
    """Load images for decals from the 'IMAGE_DECALS' dictionary and resize them."""

    decals: dict = {}
    psize2: int = 2 * psize

    for k, v in IMAGE_DECALS.items():
        decals[k] = Image.open(v)
        decals[k].thumbnail((psize2, psize2), Image.ANTIALIAS)

    return decals


def _evenqOffsetToPixel(i: int = 0, j: int = 0, size: int = None, pos: tuple = None) -> Tuple[int, int]:
    """Convert the coordinate system to the pixel-space coordinates. Use argument 'pos' to convert a position in pixel-space."""
    if size is None:
        size = SIZE
    if pos:
        i, j = pos
    x = size * 3 / 2 * i
    y = size * SQRT3 * (j - 0.5 * (i & 1))
    return int(x + size), int(y + size * 2)


def _hexagonPoints(i: int = 0, j: int = 0, size: int = None, pos: tuple = None) -> List:
    """
    Produces the points to draw an hexagon.
    Returned points are in pixel-space since arguments 'i' and 'j' need to be in pixel-space.
    Use argument 'pos' to have an hexagon centered on the position.
    """

    if size is None:
        size = SIZE

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


def _drawHexagon(img: Image, i: int, j: int, size: int = None, color: str = 'white', alpha: int = 255) -> None:
    """Draws an hexagon at the given coordinates already in pixel-space."""

    if size is None:
        size = SIZE

    draw = ImageDraw.Draw(img, 'RGBA')
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.polygon(points, fill=(r, g, b, alpha), outline=None)


def _drawHexagonBorder(img: Image, i: int, j: int, size: int = None, color: str = 'white', width: int = 1, alpha: int = 255) -> None:
    """Draws the border of an hexagon at the given coordinates in pixel-space."""

    if size is None:
        size = SIZE

    width = int(max(1, size * width * .09))

    draw = ImageDraw.Draw(img, 'RGBA')
    r, g, b = ImageColor.getrgb(color)
    points = _hexagonPoints(i, j, size)
    draw.line(points, fill=(r, g, b, alpha), width=width)


def drawHexagon(img: Image, x: int, y: int, color: str, width: int = 1, fill: str = None, alpha: int = 255, size: int = None) -> None:
    """Draws an hexagon at the given (x,y) coordinates in hex-space over the given 'img' image."""

    if size is None:
        size = SIZE

    i, j = _evenqOffsetToPixel(x, y, size)
    if fill:
        _drawHexagon(img, i, j, size, color=fill, alpha=alpha)
    _drawHexagonBorder(img, i, j, size, color, width, alpha=alpha)


def drawBoard(board: GameBoard, size: int = None) -> Image:
    """Returns an Image with only the board drawn on it."""
    if size is None:
        size = SIZE

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


def board2png(filename: str, boardName: str, format: str = 'PNG', size: int = None) -> None:
    """Draw a board and save it with a specified filename."""

    if op.exists(filename):
        return

    if size is None:
        size = SIZE

    board = parseBoard(boardName)
    img = drawBoard(board, size)
    img.save(filename, format)


def drawState(board: GameBoard, state: GameState, last_action: bool = False, size: int = None) -> Image:
    """
    Returns an Image with the board and the current state drawn on it.
    Set 'last_action' or 'utils.images.ALWAYS_ACTIONS' to TRUE to also print the action that generated the state (if any).
    """

    if size is None:
        size = SIZE

    img: Image = drawBoard(board, size)

    x, y = board.shape

    psize = int(size * .6)

    decals = _loadDecals(psize)

    if (last_action or ALWAYS_ACTIONS) and state.lastAction:
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
    """Draws a figure on the map based on its position in pixel-space (pi, pj)."""
    xy = (pi - psize, pj - psize, pi + psize, pj + psize)
    dxy = (pi - psize, pj - psize)

    draw = ImageDraw.Draw(img, 'RGBA')
    draw.ellipse(xy, fill=COLORS[figure.team])

    if figure.killed:
        psize = psize * .81
        xy = (pi - psize, pj - psize, pi + psize, pj + psize)
        draw.ellipse(xy, fill='#555555')

    if figure.stat == stat('HIDDEN'):
        decal = decals['hidden']
    else:
        decal = decals[figure.kind]
    img.paste(decal, dxy, mask=decal)


def drawAction(img: Image, action: Action, size: int = None) -> None:
    """
    Draws an action on the given image.
    Movements actions are white-ish lines.
    Attack actions are team-colored lines and consider the LOS/LOF difference.
    """
    if size is None:
        size = SIZE

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


def scenario2png(filename: str, scenario, format: str = 'PNG', size: int = None) -> None:
    """Draw a scenario and save it with a specified filename."""

    if op.exists(filename):
        return

    if size is None:
        size = SIZE

    board, state = buildScenario(scenario)
    img = drawState(board, state, size=size)
    img.save(filename, format)
