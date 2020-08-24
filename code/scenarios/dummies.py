"""All these scenarios are adapted from the main project source code."""
import numpy as np

from core import RED, BLUE
from core.figures import Infantry, Tank
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain


def _dummyBattleground(shape: tuple):
    board = GameBoard(shape)
    state = GameState(shape)

    terrain = np.zeros(shape, dtype='uint8')
    terrain[(4, 5)] = Terrain.FOREST
    terrain[(5, 5)] = Terrain.FOREST
    terrain[(5, 4)] = Terrain.FOREST

    terrain[0, :] = Terrain.ROAD

    return board, state, terrain


def scenarioDummy1() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    board, state, terrain = _dummyBattleground((10, 10))
    board.addTerrain(terrain)

    board.setObjectives((9, 9))

    state.addFigure(
        Infantry((4, 1), RED),
        Tank((4, 3), RED),
        Infantry((5, 2), BLUE)
    )

    board.name = state.name = 'scenario1'
    return board, state


def scenarioDummy2() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    board, state, terrain = _dummyBattleground((10, 20))

    terrain[:, 12:20] = Terrain.URBAN
    board.addTerrain(terrain)

    board.setObjectives((9, 9))

    state.addFigure(
        Infantry((4, 1), RED),
        Tank((4, 3), RED),
        Infantry((2, 16), BLUE, stat=HIDDEN)
    )

    board.name = state.name = 'scenario2'
    return board, state


def scenarioDummy3() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    board, state, terrain = _dummyBattleground((10, 20))

    terrain[:, 12:20] = Terrain.URBAN
    board.addTerrain(terrain)

    board.setObjectives((9, 9))

    state.addFigure(
        Infantry((4, 1), RED),
        Tank((4, 3), RED),
        Infantry((4, 14), BLUE, stat=HIDDEN)
    )

    board.name = state.name = 'scenario3'
    return board, state


def scenarioDummyResponseCheck() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    board, state, terrain = _dummyBattleground((10, 20))

    terrain[(2, 5)] = Terrain.FOREST
    terrain[(3, 5)] = Terrain.FOREST
    terrain[(6, 5)] = Terrain.FOREST
    terrain[(7, 5)] = Terrain.FOREST
    terrain[(8, 5)] = Terrain.FOREST
    terrain[(5, 4)] = Terrain.OPEN_GROUND

    terrain[:, 14:20] = Terrain.URBAN
    board.addTerrain(terrain)

    board.setObjectives((9, 12))

    state.addFigure(Infantry((4, 1), RED))
    state.addFigure(Tank((4, 3), RED))
    state.addFigure(Infantry((4, 14), BLUE, stat=HIDDEN))

    board.name = state.name = 'scenarioDummyResponseCheck'
    return board, state


def scenarioInSightTest() -> (GameBoard, GameState):
    """
    Sets up a specific scenario. reset to state of board to an initial state.
    Here this is just a dummy.
    """

    board, state, terrain = _dummyBattleground((10, 20))

    terrain[(2, 5)] = Terrain.FOREST
    terrain[(3, 5)] = Terrain.FOREST
    terrain[(6, 5)] = Terrain.FOREST
    terrain[(7, 5)] = Terrain.FOREST
    terrain[(8, 5)] = Terrain.FOREST
    terrain[(5, 4)] = Terrain.OPEN_GROUND

    terrain[:, 14:20] = Terrain.URBAN
    board.addTerrain(terrain)

    board.setObjectives((9, 12))

    state.addFigure(
        Tank((7, 10), RED),
        Tank((9, 7), RED),
        Infantry((4, 14), BLUE, stat=HIDDEN)
    )

    board.name = state.name = 'scenarioInSightTest'
    return board, state
