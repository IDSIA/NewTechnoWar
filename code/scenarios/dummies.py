"""All these scenarios are adapted from the main project source code."""
from core import RED, BLUE
from core.figures import Infantry, Tank, FigureStatus
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.state import GameState
import numpy as np

from core.game.terrain import Terrain


def scenarioDummy1() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    shape = (10, 10)
    board = GameBoard(shape)
    state = GameState(shape)

    forest = np.zeros(shape, dtype='uint8')
    forest[(4, 5)] = Terrain.FOREST
    forest[(5, 5)] = Terrain.FOREST
    forest[(5, 4)] = Terrain.FOREST
    board.addTerrain(forest)

    roads = np.zeros(shape, dtype='uint8')
    roads[0, :] = Terrain.ROAD
    board.addTerrain(roads)

    objective = np.zeros(shape, dtype='uint8')
    objective[9, 9] = 1
    board.addObjective(objective)

    state.addFigure(Infantry((4, 1), RED))
    state.addFigure(Tank((4, 3), RED))
    state.addFigure(Infantry((5, 2), BLUE))

    board.name = state.name = 'scenario1'
    return board, state


def scenarioDummy2() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    shape = (10, 20)
    board = GameBoard(shape)
    state = GameState(shape)

    forest = np.zeros(shape, dtype='uint8')
    forest[(4, 5)] = Terrain.FOREST
    forest[(5, 5)] = Terrain.FOREST
    forest[(5, 4)] = Terrain.FOREST
    board.addTerrain(forest)

    urban = np.zeros(shape, dtype='uint8')
    urban[:, 12:20] = Terrain.URBAN
    board.addTerrain(urban)

    roads = np.zeros(shape, dtype='uint8')
    roads[0, :] = Terrain.ROAD
    board.addTerrain(roads)

    objective = np.zeros(shape, dtype='uint8')
    objective[9, 9] = 1
    board.addObjective(objective)

    state.addFigure(Infantry((4, 1), RED))
    state.addFigure(Tank((4, 3), RED))
    state.addFigure(Infantry((2, 16), BLUE, stat=HIDDEN))

    board.name = state.name = 'scenario2'
    return board, state


def scenarioDummy3() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    shape = (10, 20)
    board = GameBoard(shape)
    state = GameState(shape)

    forest = np.zeros(shape, dtype='uint8')
    forest[(4, 5)] = Terrain.FOREST
    forest[(5, 5)] = Terrain.FOREST
    forest[(5, 4)] = Terrain.FOREST
    board.addTerrain(forest)

    urban = np.zeros(shape, dtype='uint8')
    urban[:, 14:20] = Terrain.URBAN
    board.addTerrain(urban)

    roads = np.zeros(shape, dtype='uint8')
    roads[0, :] = Terrain.ROAD
    board.addTerrain(roads)

    objective = np.zeros(shape, dtype='uint8')
    objective[9, 9] = 1
    board.addObjective(objective)

    state.addFigure(Infantry((4, 1), RED))
    state.addFigure(Tank((4, 3), RED))
    state.addFigure(Infantry((4, 14), BLUE, stat=HIDDEN))

    board.name = state.name = 'scenario3'
    return board, state


def scenarioDummyResponseCheck() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    shape = (10, 20)
    board = GameBoard(shape)
    state = GameState(shape)

    forest = np.zeros(shape, dtype='uint8')
    forest[(2, 5)] = Terrain.FOREST
    forest[(3, 5)] = Terrain.FOREST
    forest[(4, 5)] = Terrain.FOREST
    forest[(5, 5)] = Terrain.FOREST
    forest[(6, 5)] = Terrain.FOREST
    forest[(7, 5)] = Terrain.FOREST
    forest[(8, 5)] = Terrain.FOREST
    board.addTerrain(forest)

    urban = np.zeros(shape, dtype='uint8')
    urban[:, 14:20] = Terrain.URBAN
    board.addTerrain(urban)

    roads = np.zeros(shape, dtype='uint8')
    roads[0, :] = Terrain.ROAD
    board.addTerrain(roads)

    objective = np.zeros(shape, dtype='uint8')
    objective[9, 12] = 1
    board.addObjective(objective)

    state.addFigure(Infantry((4, 1), RED))
    state.addFigure(Tank((4, 3), RED))
    state.addFigure(Infantry((4, 14), BLUE, stat=HIDDEN))

    board.name = state.name = 'scenarioDummyResponseCheck'
    return board, state
