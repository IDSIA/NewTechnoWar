import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import RegularPolygon
from math import sqrt

from core import RED, BLUE, Terrain
from core.figures import FigureType
from core.game import GameManager

from utils.coordinates import cube_to_hex, to_cube


def draw_state(gm: GameManager, size: float = 2. / 3., coord_qr=True, coord_xyz=False):
    cols, rows = gm.shape

    fig, ax = plt.subplots(1)
    ax.set_aspect('equal')
    ax.set_xlim((-1, cols))
    ax.set_ylim((-1, rows + 2))

    for r in range(rows):
        for q in range(cols):
            p = (q, r)
            c = to_cube(p)

            print(p, c)

            # background color
            color = 'white'
            if gm.board.terrain[p] == Terrain.ROAD:
                color = 'gray'
            if gm.board.terrain[p] > Terrain.ROAD:
                color = 'pink'

            # coordinates
            x, y = convert(q, r, size)

            # draw content
            draw_hex(ax, x, y, color)
            if coord_qr:
                draw_text(ax, x, y + 0.4, f'({q},{r})')
            if coord_xyz:
                draw_text(ax, x, y + 0.2, f'({c.x},{c.y},{c.z})')

            draw_units(ax, x, y, gm, RED, p)
            draw_units(ax, x, y, gm, BLUE, p)

            if gm.board.objective[p] > 0:
                draw_text(ax, x, y + 0.25, 'X', 'orange', 10)

    return fig, ax


def draw_show(fig, ax):
    ax.invert_yaxis()
    plt.axis('off')
    plt.show()


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


def draw_units(ax, x, y, state: GameManager, agent: str, p: tuple):
    index = state.board.figures[agent][p]
    if index > -1:
        figure = state.getFigureByPos(agent, p)
        txt = 'T' if figure.kind == FigureType.VEHICLE else 'I'

        draw_hex(ax, x, y, agent, .5)
        draw_text(ax, x, y - 0.25, figure.name, agent, 4)
        draw_text(ax, x, y, txt, agent, 5)


def draw_lines(ax, line, size=2. / 3.):
    for hex in line:
        if len(hex) > 2:
            hex = cube_to_hex(hex)
        x, y = convert(*(hex), size)
        draw_hex(ax, x, y, 'green')

    return ax
