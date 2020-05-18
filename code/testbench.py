# %% imports

import matplotlib.pyplot as plt
import numpy as np

from core import RED, BLUE, Terrain
from core.agents import Agent, Parameters
from core.figures import Infantry, Tank
from core.game.__init__ import GameManager
from core.game.scenarios import scenarioTestBench
from utils.coordinates import cube_distance, cube_linedraw, to_cube, cube_to_hex
from utils.drawing import draw_state, draw_show, draw_lines

# %% initialization

plt.rcParams['figure.dpi'] = 250

shape = (10, 10)

# setting up basic agent features
redParameters = Parameters(RED, {})
blueParameters = Parameters(BLUE, {})

redAgent = Agent(1, redParameters)
blueAgent = Agent(1, blueParameters)

# %% board setup

board = scenarioTestBench()

# %% draw initial setup
draw_show(*draw_state(board))

# %% select tanks

redTank = board.getFigureByPos(RED, (0, 2))
blueTank = board.getFigureByPos(BLUE, (7, 6))

# %% compute distance between tanks

dx = cube_distance(redTank.position, blueTank.position)

# %% daraw line of sight

line = cube_linedraw(redTank.position, blueTank.position)

fig, ax = draw_state(board)
ax = draw_lines(ax, line)
draw_show(fig, ax)

# %% draw reachable area

movements = board.buildMovements(BLUE, blueTank)

fig, ax = draw_state(board)
draw_lines(ax, [a.destination for a in movements])
draw_show(fig, ax)

# %% perform move action
m = movements[0]

board.activate(m)

draw_show(*draw_state(board))

# %% action performed
print('move', m.figure.name, 'to', cube_to_hex(m.destination))

# %% perform shoot action
shoots = board.buildShoots(BLUE, blueTank)
s = shoots[0]

print(BLUE, 'shoots', s.figure.name, 'against', s.target.name, 'with', s.weapon.name)


# %%

board.hashValue()


# %%

board.whoWon()

# %%

blueTank.goto(to_cube((5, 5)))
board.whoWon()


# %%

borders = [
    (0, 0, 0, 9),
    (0, 9, 9, 9),
    (9, 9, 9, 0),
    (9, 0, 0, 0),

    (1, 0, 8, 0),
    (9, 1, 9, 8),
    (1, 9, 8, 9),
    (0, 8, 0, 1),

    (2, 9, 8, 9),
    (2, 9, 8, 9),
    (1, 0, 8, 0),
    (2, 0, 8, 0),
]

for sx, sy, ex, ey in borders:
    line = cube_linedraw(to_cube((sx, sy)), to_cube((ex, ey)))

    fig, ax = draw_state(board)
    ax = draw_lines(ax, line)
    draw_show(fig, ax)
