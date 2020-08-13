import numpy as np

from core import RED, BLUE
from core.figures import Infantry, Tank
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import fillLine


# TODO: maybe define a class with a win condition?


def _battleground16x16() -> GameBoard:
    shape = (16, 16)
    board: GameBoard = GameBoard(shape)

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

    board.addTerrain(terrain)

    objective = np.zeros(shape, dtype='uint8')
    objective[8, 8] = 1
    board.addObjective(objective)

    return board


def scenarioTestBench() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(Infantry((3, 1), RED, 'rInf1'))
    state.addFigure(Infantry((7, 2), RED, 'rInf2'))
    state.addFigure(Infantry((6, 2), RED, 'rInf3'))
    state.addFigure(Infantry((1, 4), RED, 'rInf4'))

    state.addFigure(Tank((2, 3), RED, 'rTank1'))
    state.addFigure(Tank((2, 1), RED, 'rTank2'))

    state.addFigure(Infantry((14, 14), BLUE, 'bInf1'))
    state.addFigure(Infantry((13, 10), BLUE, 'bInf2'))
    state.addFigure(Infantry((9, 13), BLUE, 'bInf3'))

    state.addFigure(Tank((12, 12), BLUE, 'bTank1'))

    board.name = state.name = "TestBench"

    return board, state


def scenarioTest1v1() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(Tank((2, 3), RED, 'Tank1'))
    state.addFigure(Tank((12, 12), BLUE, 'Tank2'))

    board.name = state.name = "1Rv1B"

    return board, state


def scenarioTest2v2() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(Tank((2, 2), RED, 'Tank1'))
    state.addFigure(Tank((3, 3), RED, 'Tank2'))

    state.addFigure(Tank((11, 11), BLUE, 'Tank3'))
    state.addFigure(Tank((12, 12), BLUE, 'Tank4'))

    board.name = state.name = "1Rv1B"

    return board, state


def scenarioTest3v1() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(Infantry((3, 1), RED, 'Inf1'))
    state.addFigure(Infantry((7, 2), RED, 'Inf2'))
    state.addFigure(Tank((2, 3), RED, 'Tank1'))

    state.addFigure(Tank((12, 12), BLUE, 'Tank2', HIDDEN))

    board.name = state.name = "3Rv1B"

    return board, state
