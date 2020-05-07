# %%
from utils.coordinates import *
from core import RED, BLUE
from core.figures import Infantry, Tank
from core.agents import Agent, Parameters
from core.state import StateOfTheBoard
from utils.coordinates import cube_distance, cube_linedraw, cube_reachable, to_cube
import numpy as np
import matplotlib.pyplot as plt

from utils.drawing import draw_state, draw_show, draw_lines

plt.rcParams['figure.dpi'] = 250

shape = (10, 10)

# setting up basic agent features
redParameters = Parameters(RED, {})
blueParameters = Parameters(BLUE, {})

redAgent = Agent(1, redParameters)
blueAgent = Agent(1, blueParameters)

# %%

board = StateOfTheBoard(shape)

obstacles = np.zeros(shape, dtype='uint8')
obstacles[4, 3:7] = 1
obstacles[5:7, 3] = 1
board.addObstacle(obstacles)

roads = np.zeros(shape, dtype='uint8')
roads[0, :] = 1
roads[:, 4] = 1
board.addRoads(roads)

objective = np.zeros(shape, dtype='uint8')
objective[5, 5] = 1
board.addObjective(objective)

board.addFigure(RED, Infantry(position=(1, 1), name='rInf1'))
board.addFigure(RED, Infantry(position=(1, 2), name='rInf2'))
board.addFigure(RED, Tank(position=(0, 2), name='rTank1'))
board.addFigure(BLUE, Infantry(position=(9, 8), name='bInf1'))
board.addFigure(BLUE, Tank(position=(5, 4), name='bTank1'))

# board.print()
fig, ax = draw_state(board)
draw_show(fig, ax)


# %%

redTank = board.getFigureByPos(RED, (0, 2))
blueTank = board.getFigureByPos(BLUE, (5, 4))

# %%

cube_distance(redTank.cube, blueTank.cube)

# %%

line = cube_linedraw(redTank.cube, blueTank.cube)

fig, ax = draw_state(board)
ax = draw_lines(ax, line)
draw_show(fig, ax)

# %%

# %%
obs = np.array(board.board.obstacles.nonzero()).T
obs = {to_cube(o) for o in obs}

cubes = cube_reachable(blueTank.cube, 3, obs)

fig, ax = draw_state(board)
ax = draw_lines(ax, cubes)
draw_show(fig, ax)


# %%
