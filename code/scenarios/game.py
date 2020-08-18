"""All these scenarios are adapted from the main project source code."""
import numpy as np

from core import RED, BLUE
from core.figures import Tank, Infantry
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import basicForest, basicUrban, basicRoad


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
    forest[19, 8] = Terrain.FOREST
    forest[18, 8] = Terrain.FOREST
    forest[17, 9] = Terrain.FOREST
    forest[16, 9:10].fill(Terrain.FOREST)
    forest[15, 10] = Terrain.FOREST

    forest[23, 14] = Terrain.FOREST
    forest[27, 18] = Terrain.FOREST

    urban[28, 15] = Terrain.URBAN

    board.addTerrain(forest)
    board.addTerrain(urban)
    board.addTerrain(road)

    objective = np.zeros(shape, dtype='uint8')
    objective[(30, 13)] = 1

    board.addObjective(objective)

    # setup dynamic parameters
    state.turn_max = 9

    state.addFigure(Tank((8, 0), RED))
    state.addFigure(Tank((7, 11), RED))
    state.addFigure(Tank((17, 20), RED))
    state.addFigure(Infantry((6, 12), RED))
    state.addFigure(Infantry((25, 22), RED))
    state.addFigure(Infantry((17, 17), RED))

    state.addFigure(Tank((33, 9), BLUE))
    state.addFigure(Infantry((34, 14), BLUE))
    state.addFigure(Infantry((34, 16), BLUE))

    # TODO: blue can place its figures

    board.name = state.name = 'junction'

    return board, state
