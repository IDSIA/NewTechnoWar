# %% imports

import matplotlib.pyplot as plt

from core import RED, BLUE
from core.game.scenarios import scenarioTestBench
from utils.coordinates import cube_distance, cube_linedraw, cube_to_hex
from utils.drawing import draw_state, draw_show, draw_lines
# %% initialization
from utils.pathfinding import findPath, reachablePath

plt.rcParams['figure.dpi'] = 250

shape = (10, 10)

gm = scenarioTestBench()

redTank = gm.getFiguresByPos(RED, (0, 2))[0]
blueTank = gm.getFiguresByPos(BLUE, (7, 6))[0]

# %% draw initial setup
fig, ax = draw_state(gm)
draw_show(fig, ax)

# %%
reachable = reachablePath(blueTank.position, gm.board, blueTank.kind, 1)

fig, ax = draw_state(gm)
ax = draw_lines(ax, reachable)
draw_show(fig, ax)

# %% draw reachable area
movements = gm.buildMovements(BLUE, blueTank)

fig, ax = draw_state(gm)
draw_lines(ax, [a.destination for a in movements])
draw_show(fig, ax)

# %% perform move action
m = movements[0]

gm.activate(m)

draw_show(*draw_state(gm))

# %% action performed
print('move', m.figure.name, 'to', cube_to_hex(m.destination))

# %% compute distance between tanks
dx = cube_distance(redTank.position, blueTank.position)

# %% daraw line of sight
line = cube_linedraw(redTank.position, blueTank.position)

fig, ax = draw_state(gm)
ax = draw_lines(ax, line)
draw_show(fig, ax)

# %% perform shoot action
# TODO: find doable shooting
"""
shoots = gm.buildShoots(BLUE, blueTank)
s = shoots[0]

print(BLUE, 'shoots', s.figure.name, 'against', s.target.name, 'with', s.weapon.name)
"""

# %%
"""
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

    (8, 9, 2, 9),
    (8, 9, 2, 9),
    (8, 0, 1, 0),
    (8, 0, 2, 0),
]

for sx, sy, ex, ey in borders:
    line = cube_linedraw(to_cube((sx, sy)), to_cube((ex, ey)))

    fig, ax = draw_state(gm)
    ax = draw_lines(ax, line)
    draw_show(fig, ax)
"""
# %%
path = findPath(redTank.position, blueTank.position, gm.board, blueTank.kind)

# %%
fig, ax = draw_state(gm)
ax = draw_lines(ax, path)
draw_show(fig, ax)
