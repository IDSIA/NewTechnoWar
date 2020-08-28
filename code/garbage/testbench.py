# %% imports

import matplotlib.pyplot as plt

from agents.matchmanager import MatchManager
from agents.players import PlayerDummy
from core import RED, BLUE
from core.game.pathfinding import findPath, reachablePath
from scenarios import scenarioTestBench
from utils.coordinates import cube_distance, cube_linedraw, cube_to_hex, to_cube
from utils.drawing import draw_state, draw_show, draw_hex_line, draw_line, fig2img

# %% initialization
plt.rcParams['figure.dpi'] = 100
plt.rcParams['figure.figsize'] = (8, 8)

board, state = scenarioTestBench()
mm: MatchManager = MatchManager('', board, state, PlayerDummy(RED), PlayerDummy(BLUE))
gm = mm.gm

redTank = state.getFiguresByPos(RED, (2, 1))[0]
blueTank = state.getFiguresByPos(BLUE, (12, 12))[0]

# %% draw initial setup
_, ax = draw_state(board, state)
im = draw_show(ax, title="Initial setup")

# %%
images = [fig2img(im)]

for i in range(1, 7):
    reachable, paths = reachablePath(blueTank, board, i)

    fig, ax = draw_state(board, state)
    ax = draw_hex_line(ax, reachable)

    for path in paths:
        draw_line(ax, path)

    im = draw_show(ax, title=f"{blueTank} range {i}")

    images.append(fig2img(im))

"""
images[0].save("BlueTankMovement.gif", save_all=True, append_images=images[1:], optimize=False, duration=600, loop=0)
"""

# %%
for i in range(1, 7):
    reachable, paths = reachablePath(redTank, board, i)

    _, ax = draw_state(board, state)
    ax = draw_hex_line(ax, reachable)

    for path in paths:
        draw_line(ax, path)

    draw_show(ax, title=f"{redTank} range {i}")

# %% compute reachable area
movements = gm.buildMovements(board, state, blueTank)

# %% draw reachable area
_, ax = draw_state(board, state)
for a in movements:
    draw_hex_line(ax, a.destination)
draw_show(ax)

# %% perform move action
m = movements[0]

state1, outcome = gm.activate(board, state, m)

draw_show(draw_state(board, state1)[1])

# %% action performed
print('move', m.figure.name, 'to', cube_to_hex(m.destination))

# %% compute distance between tanks
dx = cube_distance(redTank.position, blueTank.position)

# %% draw line of sight
line = cube_linedraw(redTank.position, blueTank.position)

fig, ax = draw_state(board, state)
ax = draw_hex_line(ax, line)
draw_show(fig, ax)

# %% perform shoot action
# TODO: find doable shooting

attacks = gm.buildAttacks(board, state, blueTank)
s = attacks[0]

print(BLUE, 'shoots', s.figure.name, 'against', s.target.name, 'with', s.weapon.name)

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

    (8, 9, 2, 9),
    (8, 9, 2, 9),
    (8, 0, 1, 0),
    (8, 0, 2, 0),
]

for sx, sy, ex, ey in borders:
    line = cube_linedraw(to_cube((sx, sy)), to_cube((ex, ey)))

    fig, ax = draw_state(board, state)
    ax = draw_hex_line(ax, line)
    draw_show(fig, ax)

# %%
path = findPath(redTank.position, blueTank.position, board, blueTank.kind)

# %%
fig, ax = draw_state(board, state)
ax = draw_hex_line(ax, path)
draw_show(fig, ax)