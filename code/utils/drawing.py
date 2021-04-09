from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import RegularPolygon

from core.const import RED, BLUE
from core.figures import FigureType
from core.game.manager import GameBoard, GameState
from core.game.terrain import Terrain
from core.utils.coordinates import Hex


# TODO: this class is old and broken!

def draw_void(board: GameBoard):
    cols, rows = board.shape

    fig = plt.figure()
    ax = plt.axes(xlim=(-1, cols), ylim=(-1, rows + 4), aspect='equal')

    return fig, ax


def draw_state(board: GameBoard, state: GameState, size: float = 2. / 3., coord_qr=True, coord_xyz=False, fig=None,
               ax=None):
    cols, rows = board.shape

    if not fig:
        fig = plt.figure()

    if not ax:
        fig, ax = draw_void(board)

    for r in range(rows):
        for q in range(cols):
            p = Hex(q, r)
            c = p.cube()

            # background color
            color = 'white'
            if board.terrain[p] == Terrain.ROAD:
                color = 'gray'
            if board.terrain[p] > Terrain.ROAD:
                color = 'pink'

            # coordinates
            x, y = convert(q, r, size)

            # draw content
            draw_hex(ax, x, y, color)
            if coord_qr:
                draw_text(ax, x, y + 0.4, f'({q},{r})')
            if coord_xyz:
                draw_text(ax, x, y + 0.2, f'({c.x},{c.y},{c.z})')

            draw_units(ax, x, y, state, RED, p)
            draw_units(ax, x, y, state, BLUE, p)

            if board.objective[p] > 0:
                draw_text(ax, x, y + 0.25, 'X', 'orange', 10)

    return fig, ax


def draw_show(ax, title=None):
    ax.invert_yaxis()
    plt.axis('off')
    if title:
        plt.title(title)
    im = plt.gcf()
    plt.show()
    return im


def convert(q, r, size=2. / 3.):
    x = size * 3. / 2 * q
    y = size * (sqrt(3) / 2 * ((q + 1) % 2) + sqrt(3) * r)
    return x, y


def draw_hex(ax, x, y, color, alpha=.9):
    h = RegularPolygon((x, y), numVertices=6, radius=2. / 3., orientation=np.radians(30), edgecolor='k',
                       facecolor=color, alpha=alpha)
    ax.add_patch(h)


def draw_text(ax, x, y, text, color='black', size=3):
    ax.text(x, y, text, ha='center', va='center', color=color, size=size)


def draw_units(ax, x, y, state: GameState, team: str, p: tuple):
    figures = state.getFiguresByPos(team, p)
    for figure in figures:
        txt = 'T' if figure.kind == FigureType.VEHICLE else 'I'

        draw_hex(ax, x, y, team, .5)
        draw_text(ax, x, y - 0.25, figure.name, team, 4)
        draw_text(ax, x, y, txt, team, 5)


def draw_hex_line(ax, line, size=2. / 3., color='green'):
    for h in line:
        if len(h) > 2:
            h = h.hex()
        x, y = convert(*(h), size)
        draw_hex(ax, x, y, color, alpha=0.6)

    return ax


def draw_line(ax, line, size=2. / 3.):
    for i in range(0, len(line) - 1):
        h1, h2 = line[i: i + 2]
        if len(h1) > 2:
            h1 = h1.hex()
        if len(h2) > 2:
            h2 = h2.hex()
        x1, y1 = convert(*(h1), size)
        x2, y2 = convert(*(h2), size)

        ax.plot([x1, x2], [y1, y2], 'yo-')


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img
