import numpy as np

from core.const import RED, BLUE
from core.figures import Infantry, Tank, Exoskeleton, Sniper, Civilian
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.goals import GoalReachPoint, GoalEliminateOpponent, GoalMaxTurn, GoalDefendPoint
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import fillLine


def _battleground16x16() -> GameBoard:
    shape = (16, 16)
    board: GameBoard = GameBoard(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (6, 3), (6, 5), Terrain.URBAN)
    fillLine(terrain, (8, 12), (12, 10), Terrain.URBAN)
    fillLine(terrain, (9, 13), (14, 10), Terrain.URBAN)
    fillLine(terrain, (10, 13), (14, 11), Terrain.URBAN)
    fillLine(terrain, (11, 14), (15, 12), Terrain.URBAN)
    fillLine(terrain, (11, 15), (13, 14), Terrain.URBAN)
    terrain[5, 3] = Terrain.URBAN

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

    # fillLine(terrain, (6, 11), (8, 10), Terrain.BUILDING)
    # fillLine(terrain, (6, 11), (6, 13), Terrain.BUILDING)
    # fillLine(terrain, (11, 9), (14, 7), Terrain.BUILDING)

    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (8, 8)),
        GoalDefendPoint(BLUE, RED, board.shape, (8, 8)),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
        GoalMaxTurn(BLUE, 12)
    )

    return board


def scenarioTestBench() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(
        Infantry((3, 1), RED, 'rInf1'),
        Infantry((7, 2), RED, 'rInf2'),
        Infantry((6, 2), RED, 'rInf3'),
        Infantry((1, 4), RED, 'rInf4'),

        Tank((2, 3), RED, 'rTank1'),
        Tank((2, 1), RED, 'rTank2'),

        Infantry((14, 14), BLUE, 'bInf1'),
        Infantry((13, 10), BLUE, 'bInf2'),
        Infantry((9, 13), BLUE, 'bInf3', stat=HIDDEN),

        Tank((12, 12), BLUE, 'bTank1', stat=HIDDEN),
    )

    board.name = state.name = "TestBench"

    return board, state


def scenarioTest1v1() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(
        Tank((2, 3), RED, 'Tank1'),
        Tank((12, 12), BLUE, 'Tank2')
    )

    board.name = state.name = "1Rv1B"

    return board, state


def scenarioTest2v2() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(
        Tank((2, 2), RED, 'Tank1'),
        Tank((3, 3), RED, 'Tank2'),

        Tank((11, 11), BLUE, 'Tank3'),
        Tank((12, 12), BLUE, 'Tank4'),
    )

    board.name = state.name = "1Rv1B"

    return board, state


def scenarioTest3v1() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(
        Infantry((3, 1), RED, 'Inf1'),
        Infantry((7, 2), RED, 'Inf2'),
        Tank((2, 3), RED, 'Tank1'),

        Tank((12, 12), BLUE, 'Tank2', HIDDEN)
    )

    board.name = state.name = "3Rv1B"

    return board, state


def scenarioTestInfantry() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    state.addFigure(
        Infantry((5, 2), RED, 'rInf1'),
        Infantry((6, 2), RED, 'rInf2'),
        Exoskeleton((5, 3), RED, 'rExo1'),
        Exoskeleton((4, 4), RED, 'rExo2'),
        Sniper((5, 3), RED, 'rSniper'),

        Infantry((11, 13), BLUE, 'bInf1'),
        Infantry((14, 8), BLUE, 'bInf2'),
        Exoskeleton((14, 10), BLUE, 'bExo1'),
        Exoskeleton((10, 11), BLUE, 'bExo2'),
        Sniper((11, 12), BLUE, 'bSniper')
    )

    board.name = state.name = "Infantry"

    return board, state


def scenarioTestLoaded() -> (GameBoard, GameState):
    board: GameBoard = _battleground16x16()
    state: GameState = GameState(board.shape)

    t1 = Tank((4, 4), RED, 'rTank1')
    i11 = Infantry((4, 4), RED, 'rInf1')
    i12 = Infantry((4, 4), RED, 'rInf2')

    t2 = Tank((12, 12), BLUE, 'bTank1')

    state.addFigure(t1, i11, i12, t2)
    t1.transportLoad(i11)
    t1.transportLoad(i12)

    board.name = state.name = "loaded"

    return board, state


def scenarioTest1v1Race() -> (GameBoard, GameState):
    shape = (17, 17)
    board: GameBoard = GameBoard(shape)
    state: GameState = GameState(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (8, 0), (8, 16), Terrain.BUILDING)
    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (3, 16)),
        GoalReachPoint(BLUE, board.shape, (13, 16)),
        GoalMaxTurn(BLUE, 12)
    )

    state.addFigure(
        Tank((3, 0), RED, 'Tank1'),
        Tank((13, 0), BLUE, 'Tank2')
    )

    board.name = state.name = "1Rv1BRace"

    return board, state


def scenarioTest1v1ArmedRace() -> (GameBoard, GameState):
    shape = (16, 16)
    board: GameBoard = GameBoard(shape)
    state: GameState = GameState(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (0, 5), (11, 0), Terrain.ISOLATED_TREE)
    fillLine(terrain, (3, 4), (15, 10), Terrain.ISOLATED_TREE)
    fillLine(terrain, (1, 5), (13, 11), Terrain.ISOLATED_TREE)
    fillLine(terrain, (4, 15), (15, 10), Terrain.ISOLATED_TREE)
    fillLine(terrain, (0, 0), (8, 4), Terrain.ROAD)
    fillLine(terrain, (8, 4), (8, 15), Terrain.ROAD)
    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (8, 8)),
        GoalDefendPoint(BLUE, RED, board.shape, (8, 8)),
        # GoalReachPoint(BLUE, board.shape, (8, 8)),
        # GoalDefendPoint(RED, BLUE, board.shape, (8, 8)),
        GoalMaxTurn(BLUE, 12)
    )

    state.addFigure(
        Infantry((1, 1), RED, 'Tank'),
        Civilian((13, 4), BLUE, 'Spotter'),
        Exoskeleton((14, 14), BLUE, 'Exo')
    )

    board.name = state.name = "1Rv1BRace"

    return board, state


def scenarioTest1v1Race() -> (GameBoard, GameState):
    shape = (17, 17)
    board: GameBoard = GameBoard(shape)
    state: GameState = GameState(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (8, 0), (8, 16), Terrain.BUILDING)
    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (3, 16)),
        GoalReachPoint(BLUE, board.shape, (13, 16)),
        GoalMaxTurn(BLUE, 12)
    )

    state.addFigure(
        Tank((3, 0), RED, 'Tank1'),
        Tank((13, 0), BLUE, 'Tank2')
    )

    board.name = state.name = "1Rv1BRace"

    return board, state


def scenarioTest1v1ArmedRace() -> (GameBoard, GameState):
    shape = (16, 16)
    board: GameBoard = GameBoard(shape)
    state: GameState = GameState(shape)

    terrain = np.zeros(shape, dtype='uint8')
    fillLine(terrain, (0, 5), (11, 0), Terrain.ISOLATED_TREE)
    fillLine(terrain, (3, 4), (15, 10), Terrain.ISOLATED_TREE)
    fillLine(terrain, (1, 5), (13, 11), Terrain.ISOLATED_TREE)
    fillLine(terrain, (4, 15), (15, 10), Terrain.ISOLATED_TREE)
    fillLine(terrain, (0, 0), (8, 4), Terrain.ROAD)
    fillLine(terrain, (8, 4), (8, 15), Terrain.ROAD)
    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (8, 8)),
        GoalDefendPoint(BLUE, RED, board.shape, (8, 8)),
        # GoalReachPoint(BLUE, board.shape, (8, 8)),
        # GoalDefendPoint(RED, BLUE, board.shape, (8, 8)),
        GoalMaxTurn(BLUE, 12)
    )

    state.addFigure(
        Infantry((1, 1), RED, 'Tank'),
        Civilian((13, 4), BLUE, 'Spotter'),
        Exoskeleton((14, 14), BLUE, 'Exo')
    )

    board.name = state.name = "1Rv1BRace"

    return board, state
