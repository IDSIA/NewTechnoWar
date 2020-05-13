# %% imports

import matplotlib.pyplot as plt
import numpy as np

from core import RED, BLUE, Terrain
from core.agents import Agent, Parameters
from core.figures import Infantry, Tank
from core.game import StateOfTheBoard
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

board = StateOfTheBoard(shape)

terrain = np.zeros(shape, dtype='uint8')
terrain[4, 3:7] = Terrain.CONCRETE_BUILDING
terrain[5:7, 3] = Terrain.CONCRETE_BUILDING
terrain[0, :] = Terrain.ROAD
terrain[:, 4] = Terrain.ROAD
board.addTerrain(terrain)

objective = np.zeros(shape, dtype='uint8')
objective[5, 5] = 1
board.addObjective(objective)

board.addFigure(RED, Infantry(position=(1, 1), name='rInf1'))
board.addFigure(RED, Infantry(position=(1, 2), name='rInf2'))
board.addFigure(RED, Tank(position=(0, 2), name='rTank1'))
board.addFigure(BLUE, Infantry(position=(9, 8), name='bInf1'))
board.addFigure(BLUE, Tank(position=(7, 6), name='bTank1'))

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
