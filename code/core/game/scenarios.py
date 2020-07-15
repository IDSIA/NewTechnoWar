import numpy as np

from core import RED, BLUE
from core.figures import Infantry, Tank
from core.game.manager import GameManager
from core.game.terrain import Terrain
from utils.coordinates import hex_linedraw, to_hex


# TODO: maybe define a class with a win condition?


def fillLine(terrain: np.ndarray, start: tuple, end: tuple, kind: int):
    if start[0] == end[0]:
        line = [(start[0], j) for j in range(start[1], end[1] + 1)]
    elif start[1] == end[1]:
        line = [(i, start[1]) for i in range(start[0], end[0] + 1)]
    else:
        line = hex_linedraw(to_hex(start), to_hex(end))
    for hex in line:
        terrain[hex] = kind


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


def battleground16x16():
    shape = (16, 16)
    gm = GameManager(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (0, 1), (5, 4), Terrain.ROAD)
    fillLine(terrain, (5, 4), (5, 8), Terrain.ROAD)
    fillLine(terrain, (0, 8), (5, 8), Terrain.ROAD)
    fillLine(terrain, (5, 8), (15, 13), Terrain.ROAD)
    fillLine(terrain, (10, 7), (15, 5), Terrain.ROAD)
    fillLine(terrain, (10, 7), (10, 10), Terrain.ROAD)
    fillLine(terrain, (2, 12), (8, 9), Terrain.ROAD)
    fillLine(terrain, (2, 12), (2, 15), Terrain.ROAD)

    terrain[9, 4] = Terrain.BUILDING
    terrain[9, 5] = Terrain.BUILDING
    terrain[10, 4] = Terrain.BUILDING

    terrain[4, 9] = Terrain.BUILDING
    terrain[3, 9] = Terrain.BUILDING
    terrain[3, 10] = Terrain.BUILDING

    terrain[6, 9] = Terrain.ISOLATED_TREE
    terrain[7, 8] = Terrain.ISOLATED_TREE
    terrain[11, 5] = Terrain.ISOLATED_TREE
    terrain[10, 11] = Terrain.ISOLATED_TREE

    fillLine(terrain, (2, 6), (4, 5), Terrain.FOREST)
    fillLine(terrain, (2, 7), (4, 6), Terrain.FOREST)
    fillLine(terrain, (9, 0), (15, 0), Terrain.FOREST)
    fillLine(terrain, (12, 1), (15, 1), Terrain.FOREST)
    fillLine(terrain, (13, 2), (14, 2), Terrain.FOREST)

    fillLine(terrain, (6, 11), (8, 10), Terrain.BUILDING)
    fillLine(terrain, (6, 11), (6, 13), Terrain.BUILDING)
    fillLine(terrain, (11, 9), (14, 7), Terrain.BUILDING)

    gm.board.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[8, 8] = 1
    gm.board.addObjective(objective)

    return gm


def scenarioTestBench():
    gm = battleground16x16()

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

    gm.name = "TestBench"

    return gm


def scenarioTest1v1():
    gm = battleground16x16()

    gm.addFigure(RED, Tank((2, 3), 'Tank1'))
    gm.addFigure(BLUE, Tank((12, 12), 'Tank2'))

    gm.name = "1Rv1B"

    return gm


def scenarioTest2v2():
    gm = battleground16x16()

    gm.addFigure(RED, Tank((2, 2), 'Tank1'))
    gm.addFigure(RED, Tank((3, 3), 'Tank2'))
    gm.addFigure(BLUE, Tank((11, 11), 'Tank3'))
    gm.addFigure(BLUE, Tank((12, 12), 'Tank4'))

    gm.name = "1Rv1B"

    return gm


def scenarioTest3v1():
    gm = battleground16x16()

    gm.addFigure(RED, Infantry((3, 1), 'Inf1'))
    gm.addFigure(RED, Infantry((7, 2), 'Inf2'))
    gm.addFigure(RED, Tank((2, 3), 'Tank1'))

    gm.addFigure(BLUE, Tank((12, 12), 'Tank2'))

    gm.name = "3Rv1B"

    return gm
