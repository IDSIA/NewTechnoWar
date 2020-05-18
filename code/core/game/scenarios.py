import numpy as np

from core import Terrain, RED, BLUE
from core.figures import Infantry, Tank
from core.game import GameManager


# TODO: maybe define a class with a win condition?

def scenario1():
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    shape = (10, 10)

    gm = GameManager(shape)

    terrain = np.zeros(shape, dtype='uint8')
    terrain[(4, 4)] = 1
    terrain[0, :] = Terrain.ROAD
    gm.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[4, 5] = 1
    gm.addObjective(objective)

    gm.addFigure(RED, Infantry((1, 1), 'rInf1'))
    gm.addFigure(RED, Tank((1, 2), 'rTank1'))
    gm.addFigure(BLUE, Infantry((3, 3), 'bInf1'))

    return gm


def scenarioTestBench():
    shape = (10, 10)
    gm = GameManager(shape)

    terrain = np.zeros(shape, dtype='uint8')
    terrain[0, :] = Terrain.ROAD
    terrain[:, 4] = Terrain.ROAD
    terrain[4, 3:7] = Terrain.CONCRETE_BUILDING
    terrain[5:7, 3] = Terrain.CONCRETE_BUILDING
    gm.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[5, 5] = 1
    gm.addObjective(objective)

    gm.addFigure(RED, Infantry(position=(1, 1), name='rInf1'))
    gm.addFigure(RED, Infantry(position=(1, 2), name='rInf2'))
    gm.addFigure(RED, Tank(position=(0, 2), name='rTank1'))

    gm.addFigure(BLUE, Infantry(position=(9, 8), name='bInf1'))
    gm.addFigure(BLUE, Tank(position=(7, 6), name='bTank1'))

    return gm
