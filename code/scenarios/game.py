"""All these scenarios are adapted from the main project source code."""
import numpy as np

from core.const import RED, BLUE
from core.figures import Tank, Infantry, APC, Exoskeleton
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.goals import GoalReachPoint, GoalEliminateOpponent, GoalMaxTurn, GoalDefendPoint
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import fillLine, MAP_SHAPE, basicTerrain


def scenarioJunction() -> (GameBoard, GameState):
    """
    Sets up scenario 'junction'.
    """
    board = GameBoard(MAP_SHAPE)
    state = GameState(MAP_SHAPE)

    # setup static parameters
    terrain = basicTerrain()

    terrain[16, 20:23] = Terrain.ISOLATED_TREE
    terrain[17, 21:24] = Terrain.ISOLATED_TREE
    terrain[20, 24:27] = Terrain.ISOLATED_TREE
    terrain[21, 24:27] = Terrain.ISOLATED_TREE

    fillLine(terrain, (15, 27), (21, 24), Terrain.ISOLATED_TREE)
    fillLine(terrain, (20, 25), (21, 25), Terrain.ISOLATED_TREE)
    fillLine(terrain, (20, 26), (21, 26), Terrain.ISOLATED_TREE)
    terrain[16, 27] = Terrain.ISOLATED_TREE

    terrain[19, 19] = Terrain.ISOLATED_TREE
    terrain[20, 18] = Terrain.ISOLATED_TREE
    terrain[21, 19] = Terrain.ISOLATED_TREE

    fillLine(terrain, (25, 21), (26, 20), Terrain.ISOLATED_TREE)
    fillLine(terrain, (25, 22), (27, 21), Terrain.ISOLATED_TREE)
    fillLine(terrain, (26, 22), (28, 21), Terrain.ISOLATED_TREE)

    terrain[23, 31] = Terrain.ISOLATED_TREE
    terrain[27, 35] = Terrain.ISOLATED_TREE

    terrain[28, 32] = Terrain.ISOLATED_TREE

    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (30, 30)),
        GoalDefendPoint(BLUE, RED, board.shape, (30, 30)),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
        GoalMaxTurn(BLUE, 10)
    )

    # setup dynamic parameters

    # orange
    i11 = Infantry((8, 17), RED, 'rInf11')
    i12 = Infantry((8, 17), RED, 'rInf12')
    t1 = Tank((8, 17), RED, 'rTank1')

    # red
    t2 = Tank((7, 28), RED, 'rTank2')
    i21 = Infantry((7, 28), RED, 'rInf21')
    i22 = Infantry((6, 29), RED, 'rInf22')

    # darkred
    t3 = Tank((17, 37), RED, 'rTank3')
    i31 = Infantry((17, 34), RED, 'rInf3')
    i32 = Infantry((25, 39), RED, 'rInf4')

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'lightred', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((33, 25), BLUE, 'bAPC1', HIDDEN),
        Infantry((36, 31), BLUE, 'bInf1', HIDDEN),
        Infantry((37, 33), BLUE, 'bInf2', HIDDEN)
    )

    t1.transportLoad(i11)
    t1.transportLoad(i12)
    t2.transportLoad(i21)

    placement_zone = np.zeros(MAP_SHAPE, dtype='uint8')
    placement_zone[28, 32:38] = 1
    placement_zone[29, 24:38] = 1
    placement_zone[30, 18:37] = 1
    placement_zone[31, 19:38] = 1
    placement_zone[32, 19:37] = 1
    placement_zone[33, 19:37] = 1
    placement_zone[34, 19:37] = 1
    placement_zone[35, 19:37] = 1
    placement_zone[36, 19:37] = 1
    placement_zone[37, 20:37] = 1
    placement_zone[38, 19:36] = 1
    placement_zone[39, 20:37] = 1
    placement_zone[40, 20:36] = 1
    placement_zone[41, 20:37] = 1
    placement_zone[42, 20:36] = 1

    state.addPlacementZone(BLUE, placement_zone)

    board.name = state.name = 'junction'

    return board, state


def scenarioJunctionExo() -> (GameBoard, GameState):
    """
    Same as scenario Junction but blue uses Exoskeletons.
    """

    board, state = scenarioJunction()

    # clear
    state.clearFigures(BLUE)

    state.addFigure(
        APC((33, 25), BLUE, 'bAPC1', HIDDEN),
        Exoskeleton((36, 31), BLUE, 'bExo1', HIDDEN),
        Exoskeleton((37, 33), BLUE, 'bExo2', HIDDEN)
    )

    board.name = state.name = 'junction-exo'

    return board, state


def scenarioRoadblock() -> (GameBoard, GameState):
    """
    Sets up scenario 'roadblock'.
    """
    board = GameBoard(MAP_SHAPE)
    state = GameState(MAP_SHAPE)
    state.turn = 4  # with initial update -> 5 (6th turn)

    # setup static parameters
    terrain = basicTerrain()

    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (43, 29)),
        GoalDefendPoint(BLUE, RED, board.shape, (43, 29)),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
        GoalMaxTurn(BLUE, 12)
    )

    # orange
    t1 = Tank((39, 22), RED, 'rTank1')
    i11 = Infantry((39, 24), RED, 'rInf11')
    i12 = Infantry((38, 26), RED, 'rInf12')

    # red
    t2 = Tank((42, 21), RED, 'rTank2')
    i21 = Infantry((42, 21), RED, 'rInf21')
    i22 = Infantry((42, 20), RED, 'rInf22')

    # darkred
    t3 = Tank((37, 21), RED, 'rTank3')
    i31 = Infantry((37, 21), RED, 'rInf31')
    i32 = Infantry((37, 21), RED, 'rInf32')

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'lightred', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((44, 27), BLUE, 'bAPC', HIDDEN),
        Infantry((43, 30), BLUE, 'bInf', HIDDEN),
    )

    t2.transportLoad(i21)
    t3.transportLoad(i31)
    t3.transportLoad(i32)

    placement_zone = np.zeros(MAP_SHAPE, dtype='uint8')
    placement_zone[42, 25:33] = 1
    placement_zone[43, 25:33] = 1
    placement_zone[44, 24:32] = 1
    placement_zone[45, 24:32] = 1

    state.addPlacementZone(BLUE, placement_zone)

    board.name = state.name = 'junction'

    return board, state


def scenarioBridgeHead() -> (GameBoard, GameState):
    """
    Sets up scenario 'bridgehead'.
    Multiple objectives.
    """
    board = GameBoard(MAP_SHAPE)
    state = GameState(MAP_SHAPE)

    # setup static parameters
    terrain = basicTerrain()

    terrain[34, 32:35] = Terrain.FOREST
    terrain[33, 32:35] = Terrain.FOREST

    terrain[34, 35:37] = Terrain.FOREST
    terrain[35, 35:38] = Terrain.FOREST
    terrain[36, 35:37] = Terrain.FOREST
    terrain[37, 36] = Terrain.FOREST

    terrain[35, 28] = Terrain.FOREST

    terrain[42, 36] = Terrain.FOREST

    terrain[38, 35:37] = Terrain.FOREST
    terrain[39, 36:37] = Terrain.FOREST
    terrain[40, 36:37] = Terrain.FOREST
    terrain[41, 37:38] = Terrain.FOREST
    terrain[42, 37:40] = Terrain.FOREST
    terrain[43, 38:40] = Terrain.FOREST
    terrain[44, 38] = Terrain.FOREST

    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (39, 29), (40, 29), (40, 30), (41, 31), (41, 32)),
        GoalDefendPoint(BLUE, RED, board.shape, (39, 29), (40, 29), (40, 30), (41, 31), (41, 32)),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
        GoalMaxTurn(BLUE, 7)
    )

    state.addChoice(RED, 'orange',
                    Tank((39, 36), RED, 'rTank1', HIDDEN),
                    Infantry((34, 32), RED, 'rInf11', HIDDEN)
                    )
    state.addChoice(RED, 'lightred',
                    Tank((37, 35), RED, 'rTank2', HIDDEN),
                    Infantry((33, 31), RED, 'rInf12', HIDDEN)
                    )
    state.addChoice(RED, 'darkred',
                    Tank((35, 33), RED, 'rTank3', HIDDEN),
                    Infantry((32, 30), RED, 'rInf21', HIDDEN)
                    )

    state.addFigure(
        APC((40, 28), BLUE, 'bAPC', HIDDEN),
        Infantry((42, 26), BLUE, 'bInf', HIDDEN),
    )

    placement_zone_red = np.zeros(MAP_SHAPE, dtype='uint8')
    placement_zone_red[28, 28:42] = 1
    placement_zone_red[29, 29:42] = 1
    placement_zone_red[30, 29:42] = 1
    placement_zone_red[31, 30:42] = 1
    placement_zone_red[32, 30:42] = 1
    placement_zone_red[33, 31:42] = 1
    placement_zone_red[34, 31:42] = 1
    placement_zone_red[35, 32:42] = 1
    placement_zone_red[36, 32:42] = 1
    placement_zone_red[37, 34:42] = 1
    placement_zone_red[38, 34:42] = 1
    placement_zone_red[39, 35:42] = 1
    placement_zone_red[40, 35:42] = 1
    placement_zone_red[41, 36:42] = 1
    placement_zone_red[42, 36:41] = 1
    placement_zone_red[43, 37:41] = 1
    placement_zone_red[44, 36:40] = 1
    placement_zone_red[45, 38:40] = 1
    placement_zone_red[46, 37:39] = 1
    placement_zone_red[47, 38] = 1

    placement_zone_blue = np.zeros(MAP_SHAPE, dtype='uint8')
    placement_zone_blue[44, 20:33] = 1
    placement_zone_blue[43, 21:34] = 1
    placement_zone_blue[42, 21:34] = 1
    placement_zone_blue[41, 22:35] = 1
    placement_zone_blue[40, 22:35] = 1
    placement_zone_blue[39, 23:35] = 1
    placement_zone_blue[38, 23:33] = 1
    placement_zone_blue[37, 24:32] = 1
    placement_zone_blue[36, 24:30] = 1
    placement_zone_blue[35, 25:30] = 1
    placement_zone_blue[34, 25:28] = 1
    placement_zone_blue[33, 26] = 1

    state.addPlacementZone(RED, placement_zone_red)
    state.addPlacementZone(BLUE, placement_zone_blue)

    board.name = state.name = 'bridgehead'

    return board, state


def scenarioCrossingTheCity() -> (GameBoard, GameState):
    """
    Sets up scenario 'CrossingTheCity'.
    """
    board = GameBoard(MAP_SHAPE)
    state = GameState(MAP_SHAPE)

    # setup static parameters
    terrain = basicTerrain()

    terrain[25, 17:20] = Terrain.FOREST
    terrain[26, 16:19] = Terrain.FOREST
    terrain[27, 18:19] = Terrain.FOREST
    terrain[28, 17:18] = Terrain.FOREST
    terrain[29, 17:18] = Terrain.FOREST
    terrain[30, 15:17] = Terrain.FOREST
    terrain[31, 16] = Terrain.FOREST

    board.addTerrain(terrain)

    board.addObjectives(
        GoalReachPoint(RED, board.shape, (39, 23)),
        GoalDefendPoint(BLUE, RED, board.shape, (39, 23)),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
        GoalMaxTurn(BLUE, 7)
    )

    # orange
    t1 = Tank((26, 16), RED, 'rTank2')
    i11 = Infantry((26, 16), RED, 'rInf21')
    i12 = Infantry((26, 16), RED, 'rInf21')

    # red 1 unit
    t2 = Tank((30, 15), RED, 'rTank3')
    i21 = Infantry((30, 15), RED, 'rInf31')
    i22 = Infantry((30, 15), RED, 'rInf31')

    # dark red 2 units
    t3 = Tank((25, 19), RED, 'rTank1')
    i31 = Infantry((25, 19), RED, 'rInf11')
    i32 = Infantry((25, 19), RED, 'rInf11')

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'lightred', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((38, 21), BLUE, 'bAPC', HIDDEN),
        Infantry((41, 23), BLUE, 'bInf', HIDDEN),
    )

    t1.transportLoad(i11)
    t1.transportLoad(i12)
    t2.transportLoad(i21)
    t2.transportLoad(i22)
    t3.transportLoad(i31)
    t3.transportLoad(i32)

    placement_zone_blue = np.zeros(MAP_SHAPE, dtype='uint8')
    placement_zone_blue[45, 17:26] = Terrain.FOREST
    placement_zone_blue[44, 17:25] = Terrain.FOREST
    placement_zone_blue[43, 17:26] = Terrain.FOREST
    placement_zone_blue[42, 17:26] = Terrain.FOREST
    placement_zone_blue[41, 18:26] = Terrain.FOREST
    placement_zone_blue[40, 17:26] = Terrain.FOREST
    placement_zone_blue[39, 18:26] = Terrain.FOREST
    placement_zone_blue[38, 17:26] = Terrain.FOREST
    placement_zone_blue[37, 18:26] = Terrain.FOREST
    placement_zone_blue[36, 18:26] = Terrain.FOREST
    placement_zone_blue[35, 24:26] = Terrain.FOREST

    state.addPlacementZone(BLUE, placement_zone_blue)

    board.name = state.name = 'crossingthecity'

    return board, state
