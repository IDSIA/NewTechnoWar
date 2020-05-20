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
    gm.board.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[4, 5] = 1
    gm.board.addObjective(objective)

    gm.addFigure(RED, Infantry((1, 1), 'rInf1'))
    gm.addFigure(RED, Tank((1, 2), 'rTank1'))
    gm.addFigure(BLUE, Infantry((3, 3), 'bInf1'))

    return gm


def blank(shape):
    gm = GameManager(shape)
    return gm


def scenarioTestBench():
    shape = (16, 16)
    gm = GameManager(shape)

    terrain = np.zeros(shape, dtype='uint8')
    terrain[0, 1] = Terrain.ROAD
    terrain[1, 2] = Terrain.ROAD
    terrain[2, 2] = Terrain.ROAD
    terrain[3, 3] = Terrain.ROAD
    terrain[4, 3] = Terrain.ROAD
    terrain[5, 4:9] = Terrain.ROAD
    terrain[0:5, 8] = Terrain.ROAD
    terrain[10, 7:10] = Terrain.ROAD
    terrain[11, 7] = Terrain.ROAD
    terrain[12, 6] = Terrain.ROAD
    terrain[13, 6] = Terrain.ROAD
    terrain[14, 5] = Terrain.ROAD
    terrain[15, 5] = Terrain.ROAD
    terrain[7, 10] = Terrain.ROAD
    terrain[6, 10] = Terrain.ROAD
    terrain[5, 11] = Terrain.ROAD
    terrain[4, 11] = Terrain.ROAD
    terrain[3, 12] = Terrain.ROAD
    terrain[2, 12:16] = Terrain.ROAD
    terrain[6, 8] = Terrain.ROAD
    terrain[7, 9] = Terrain.ROAD
    terrain[8, 9] = Terrain.ROAD
    terrain[9, 10] = Terrain.ROAD
    terrain[10, 10] = Terrain.ROAD
    terrain[11, 11] = Terrain.ROAD
    terrain[12, 11] = Terrain.ROAD
    terrain[13, 12] = Terrain.ROAD
    terrain[14, 12] = Terrain.ROAD
    terrain[15, 13] = Terrain.ROAD

    terrain[9, 4] = Terrain.CONCRETE_BUILDING
    terrain[9, 5] = Terrain.CONCRETE_BUILDING
    terrain[10, 4] = Terrain.CONCRETE_BUILDING

    terrain[4, 9] = Terrain.CONCRETE_BUILDING
    terrain[3, 9] = Terrain.CONCRETE_BUILDING
    terrain[3, 10] = Terrain.CONCRETE_BUILDING

    terrain[11, 9] = Terrain.CONCRETE_BUILDING
    terrain[12, 8] = Terrain.CONCRETE_BUILDING
    terrain[13, 8] = Terrain.CONCRETE_BUILDING
    terrain[14, 7] = Terrain.CONCRETE_BUILDING

    terrain[8, 10] = Terrain.CONCRETE_BUILDING
    terrain[7, 11] = Terrain.CONCRETE_BUILDING
    terrain[6, 11:14] = Terrain.CONCRETE_BUILDING

    gm.board.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[8, 8] = 1
    gm.board.addObjective(objective)

    gm.addFigure(RED, Infantry((3, 1), 'rInf1'))
    gm.addFigure(RED, Infantry((7, 2), 'rInf2'))
    gm.addFigure(RED, Infantry((6, 2), 'rInf3'))
    gm.addFigure(RED, Infantry((1, 4), 'rInf4'))
    gm.addFigure(RED, Tank((2, 3), 'rTank1'))
    gm.addFigure(RED, Tank((2, 1), 'rTank2'))

    gm.addFigure(BLUE, Infantry((14, 14), 'bInf1'))
    gm.addFigure(BLUE, Infantry((13, 10), 'bInf2'))
    gm.addFigure(BLUE, Infantry((9, 13), 'bInf3'))
    gm.addFigure(BLUE, Tank((12, 12), 'bTank1'))

    return gm
