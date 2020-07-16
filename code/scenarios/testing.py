import numpy as np

from core import RED, BLUE
from core.figures import Infantry, Tank
from core.figures.status import HIDDEN
from core.game.manager import GameManager
from core.game.terrain import Terrain
from scenarios.utils import fillLine


# TODO: maybe define a class with a win condition?


def _battleground16x16():
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
    gm = _battleground16x16()

    gm.addFigure(Infantry((3, 1), RED, 'rInf1'))
    gm.addFigure(Infantry((7, 2), RED, 'rInf2'))
    gm.addFigure(Infantry((6, 2), RED, 'rInf3'))
    gm.addFigure(Infantry((1, 4), RED, 'rInf4'))

    gm.addFigure(Tank((2, 3), RED, 'rTank1'))
    gm.addFigure(Tank((2, 1), RED, 'rTank2'))

    gm.addFigure(Infantry((14, 14), BLUE, 'bInf1'))
    gm.addFigure(Infantry((13, 10), BLUE, 'bInf2'))
    gm.addFigure(Infantry((9, 13), BLUE, 'bInf3'))

    gm.addFigure(Tank((12, 12), BLUE, 'bTank1'))

    gm.name = "TestBench"

    return gm


def scenarioTest1v1():
    gm = _battleground16x16()

    gm.addFigure(Tank((2, 3), RED, 'Tank1'))
    gm.addFigure(Tank((12, 12), BLUE, 'Tank2'))

    gm.name = "1Rv1B"

    return gm


def scenarioTest2v2():
    gm = _battleground16x16()

    gm.addFigure(Tank((2, 2), RED, 'Tank1'))
    gm.addFigure(Tank((3, 3), RED, 'Tank2'))

    gm.addFigure(Tank((11, 11), BLUE, 'Tank3'))
    gm.addFigure(Tank((12, 12), BLUE, 'Tank4'))

    gm.name = "1Rv1B"

    return gm


def scenarioTest3v1():
    gm = _battleground16x16()

    gm.addFigure(Infantry((3, 1), RED, 'Inf1'))
    gm.addFigure(Infantry((7, 2), RED, 'Inf2'))
    gm.addFigure(Tank((2, 3), RED, 'Tank1'))

    gm.addFigure(Tank((12, 12), BLUE, 'Tank2', HIDDEN))

    gm.name = "3Rv1B"

    return gm
