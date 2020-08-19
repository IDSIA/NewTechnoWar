"""All these scenarios are adapted from the main project source code."""
import numpy as np

from core import RED, BLUE
from core.figures import Tank, Infantry, APC
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import basicForest, basicUrban, basicRoad, fillLine


def scenarioJunction() -> (GameBoard, GameState):
    """
    Sets up scenario 'junction'.
    """
    shape = (52, 25)  # entire map: 52x42
    board = GameBoard(shape)
    state = GameState(shape)

    # setup static parameters
    forest = basicForest()
    urban = basicUrban()
    road = basicRoad()

    forest[16, 3:6].fill(Terrain.FOREST)
    forest[17, 4:7].fill(Terrain.FOREST)
    forest[20, 7:10].fill(Terrain.FOREST)
    forest[21, 7:10].fill(Terrain.FOREST)

    fillLine(forest, (15, 10), (21, 7), Terrain.FOREST)
    fillLine(forest, (20, 8), (21, 8), Terrain.FOREST)
    fillLine(forest, (20, 9), (21, 9), Terrain.FOREST)
    forest[16, 10] = Terrain.FOREST

    forest[19, 2] = Terrain.FOREST
    forest[20, 1] = Terrain.FOREST
    forest[21, 2] = Terrain.FOREST

    fillLine(forest, (25, 4), (26, 3), Terrain.FOREST)
    fillLine(forest, (25, 5), (27, 4), Terrain.FOREST)
    fillLine(forest, (26, 5), (28, 4), Terrain.FOREST)

    forest[23, 14] = Terrain.ISOLATED_TREE
    forest[27, 18] = Terrain.ISOLATED_TREE

    forest[28, 15] = Terrain.ISOLATED_TREE

    board.addTerrain(forest)
    board.addTerrain(urban)
    board.addTerrain(road)

    objective = np.zeros(shape, dtype='uint8')
    objective[(30, 13)] = 1

    board.addObjective(objective)

    # setup dynamic parameters
    state.turn_max = 9

    rt1 = Tank((8, 0), RED, 'rTank1')
    rt2 = Tank((7, 11), RED, 'rTank2')
    rt3 = Tank((17, 20), RED, 'rTank3')

    i11 = Infantry((8, 0), RED, 'rInf11')
    i12 = Infantry((8, 0), RED, 'rInf12')
    i21 = Infantry((7, 11), RED, 'rInf21')
    i22 = Infantry((6, 12), RED, 'rInf22')
    i3 = Infantry((17, 17), RED, 'rInf3')
    i4 = Infantry((25, 22), RED, 'rInf4')

    rt1.transportLoad(i11)
    rt1.transportLoad(i12)
    rt2.transportLoad(i21)

    state.addFigure(rt1, rt2, rt3, i11, i12, i21, i22, i3, i4)

    state.addFigure(
        APC((33, 8), BLUE, 'bACP1', HIDDEN),
        Infantry((36, 14), BLUE, 'bInf1', HIDDEN),
        Infantry((37, 16), BLUE, 'bInf2', HIDDEN)
    )

    # TODO: blue can place its figures

    board.name = state.name = 'junction'

    return board, state
