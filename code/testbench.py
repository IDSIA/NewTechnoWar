# %%
from utils.coordinates import hex_distance
from utils.coordinates import hex_linedraw, to_hex
import numpy as np
from core.state import StateOfTheBoard
from core.agents import Agent, Parameters
from core.figures import Infantry, Tank

# setting up basic agent features
redParameters = Parameters('red', {})
blueParameters = Parameters('blue', {})

redAgent = Agent(1, redParameters)
blueAgent = Agent(1, blueParameters)

# %%
shape = (10, 10)
board = StateOfTheBoard(shape, redAgent.team, blueAgent.team)

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

board.addFigure('red', Infantry(position=(1, 1), name='rInf1'))
board.addFigure('red', Infantry(position=(1, 2), name='rInf2'))
board.addFigure('red', Tank(position=(0, 2), name='rTank1'))
board.addFigure('blue', Infantry(position=(9, 8), name='bInf1'))
board.addFigure('blue', Tank(position=(7, 7), name='bTank1'))

board.print()

# %%

redTank = board.getFigureByPos('red', (0, 2))
blueTank = board.getFigureByPos('blue', (7, 7))

# %%

hex_distance(to_hex(redTank.position), to_hex(blueTank.position))

# %%

line = hex_linedraw(to_hex(redTank.position), to_hex(blueTank.position))

board.print(extra=line)

# %%


# %%
