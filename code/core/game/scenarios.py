import numpy as np

from core import Terrain, RED, BLUE
from core.figures import Infantry, Tank
from core.game import GameManager
from utils.coordinates import to_cube


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

    gm.addFigure(RED, Infantry(to_cube((1, 1)), name='rInf1'))
    gm.addFigure(RED, Tank(to_cube((1, 2)), name='rTank1'))
    gm.addFigure(BLUE, Infantry(to_cube((3, 3)), name='bInf1'))

    return gm
