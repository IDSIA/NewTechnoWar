# %%
import numpy as np
from core.state import StateOfTheBoard
from core.agents import Agent, Parameters
from core.figures import TYPE_VEHICLE, Infantry, Tank
from utils.colors import red, blue, yellow, pinkBg, grayBg, blackBg

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
board.addFigure('red', Infantry(position=(1, 2), name='rInf1'))
board.addFigure('red', Tank(position=(0, 2), name='rTank1'))
board.addFigure('blue', Infantry(position=(9, 8), name='bInf1'))
board.addFigure('blue', Infantry(position=(7, 7), name='bInf1'))

board.print()

# %%
