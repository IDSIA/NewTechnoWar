"""All these scenarios are adapted from the main project source code."""
import numpy as np

from core import RED, BLUE
from core.figures import Tank, Infantry, APC, Exoskeleton
from core.figures.status import HIDDEN
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from scenarios.utils import basicForest, basicUrban, basicRoad, fillLine

shape = (52, 25)  # entire map: 52x42


def scenarioJunction() -> (GameBoard, GameState):
    """
    Sets up scenario 'junction'.
    """
    board = GameBoard(shape)
    state = GameState(shape)

    # setup static parameters
    terrain = np.zeros(shape, dtype='uint8')
    basicForest(terrain)
    basicUrban(terrain)
    basicRoad(terrain)

    terrain[16, 3:6] = Terrain.FOREST
    terrain[17, 4:7] = Terrain.FOREST
    terrain[20, 7:10] = Terrain.FOREST
    terrain[21, 7:10] = Terrain.FOREST

    fillLine(terrain, (15, 10), (21, 7), Terrain.FOREST)
    fillLine(terrain, (20, 8), (21, 8), Terrain.FOREST)
    fillLine(terrain, (20, 9), (21, 9), Terrain.FOREST)
    terrain[16, 10] = Terrain.FOREST

    terrain[19, 2] = Terrain.FOREST
    terrain[20, 1] = Terrain.FOREST
    terrain[21, 2] = Terrain.FOREST

    fillLine(terrain, (25, 4), (26, 3), Terrain.FOREST)
    fillLine(terrain, (25, 5), (27, 4), Terrain.FOREST)
    fillLine(terrain, (26, 5), (28, 4), Terrain.FOREST)

    terrain[23, 14] = Terrain.ISOLATED_TREE
    terrain[27, 18] = Terrain.ISOLATED_TREE

    terrain[28, 15] = Terrain.ISOLATED_TREE

    board.addTerrain(terrain)

    board.setObjectives((30, 13))

    # setup dynamic parameters
    state.turn_max = 9

    # orange
    i11 = Infantry((8, 0), RED, 'rInf11')
    i12 = Infantry((8, 0), RED, 'rInf12')
    t1 = Tank((8, 0), RED, 'rTank1')
    t1.transportLoad(i11)
    t1.transportLoad(i12)

    # red
    t2 = Tank((7, 11), RED, 'rTank2')
    i21 = Infantry((7, 11), RED, 'rInf21')
    i22 = Infantry((6, 12), RED, 'rInf22')
    t2.transportLoad(i21)

    # darkred
    t3 = Tank((17, 20), RED, 'rTank3')
    i31 = Infantry((17, 17), RED, 'rInf3')
    i32 = Infantry((25, 22), RED, 'rInf4')

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'red', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((33, 8), BLUE, 'bAPC1', HIDDEN),
        Infantry((36, 14), BLUE, 'bInf1', HIDDEN),
        Infantry((37, 16), BLUE, 'bInf2', HIDDEN)
    )

    placement_zone = np.zeros(shape, dtype='uint8')
    placement_zone[28, 15:21] = 1
    placement_zone[29, 7:21] = 1
    placement_zone[30, 2:20] = 1
    placement_zone[31, 2:21] = 1
    placement_zone[32, 2:20] = 1
    placement_zone[33, 2:20] = 1
    placement_zone[34, 2:20] = 1
    placement_zone[35, 2:19] = 1
    placement_zone[36, 2:20] = 1
    placement_zone[37, 3:20] = 1
    placement_zone[38, 2:19] = 1
    placement_zone[39, 3:20] = 1
    placement_zone[40, 3:19] = 1
    placement_zone[41, 3:20] = 1
    placement_zone[42, 3:19] = 1

    board.addPlacementZone(BLUE, placement_zone)

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
        APC((33, 8), BLUE, 'bAPC1', HIDDEN),
        Exoskeleton((36, 14), BLUE, 'bExo1', HIDDEN),
        Exoskeleton((37, 16), BLUE, 'bExo2', HIDDEN)
    )

    board.name = state.name = 'junction-exo'

    return board, state


def scenarioRoadblock() -> (GameBoard, GameState):
    """
    Sets up scenario 'roadblock'.
    """
    board = GameBoard(shape)
    state = GameState(shape)
    state.turn = 4  # with initial update -> 5 (6th turn)
    state.turn_max = 12

    # setup static parameters
    terrain = np.zeros(shape, dtype='uint8')
    basicForest(terrain)
    basicUrban(terrain)
    basicRoad(terrain)

    board.addTerrain(terrain)

    board.setObjectives((43, 12))

    # orange
    t1 = Tank((37, 4), RED, 'rTank2')
    i11 = Infantry((37, 6), RED, 'rInf21')
    i12 = Infantry((36, 8), RED, 'rInf22')

    # red
    t2 = Tank((42, 4), RED, 'rTank3')
    i21 = Infantry((42, 4), RED, 'rInf31')
    i22 = Infantry((42, 3), RED, 'rInf32')
    t2.transportLoad(i21)

    # darkred
    i31 = Infantry((39, 5), RED, 'rInf11')
    i32 = Infantry((39, 5), RED, 'rInf12')
    t3 = Tank((39, 5), RED, 'rTank1')
    t3.transportLoad(i31)
    t3.transportLoad(i32)

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'red', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((43, 15), BLUE, 'bAPC', HIDDEN),
        Infantry((42, 18), BLUE, 'bInf', HIDDEN),
    )

    placement_zone = np.zeros(shape, dtype='uint8')
    placement_zone[42, 8:16] = 1
    placement_zone[43, 8:16] = 1
    placement_zone[44, 7:15] = 1
    placement_zone[45, 7:15] = 1

    board.addPlacementZone(BLUE, placement_zone)

    board.name = state.name = 'junction'

    return board, state


def scenarioBridgeHead() -> (GameBoard, GameState):
    """
    Sets up scenario 'bridgehead'.
    Multiple objectives.
    """
    board = GameBoard(shape)
    state = GameState(shape)
    state.turn_max = 6

    # setup static parameters
    terrain = np.zeros(shape, dtype='uint8')
    basicForest(terrain)
    basicUrban(terrain)
    basicRoad(terrain)

    terrain[34, 15:18] = Terrain.FOREST
    terrain[33, 15:18] = Terrain.FOREST

    terrain[34, 18:20] = Terrain.FOREST
    terrain[35, 18:21] = Terrain.FOREST
    terrain[36, 18:20] = Terrain.FOREST
    terrain[37, 19] = Terrain.FOREST

    terrain[35, 11] = Terrain.FOREST

    terrain[42, 19] = Terrain.FOREST

    terrain[38, 18:20] = Terrain.FOREST
    terrain[39, 19:20] = Terrain.FOREST
    terrain[40, 19:20] = Terrain.FOREST
    terrain[41, 20:21] = Terrain.FOREST
    terrain[42, 20:23] = Terrain.FOREST
    terrain[43, 21:23] = Terrain.FOREST
    terrain[44, 21] = Terrain.FOREST

    board.addTerrain(terrain)

    board.setObjectives((39, 12), (40, 12), (40, 13), (41, 14), (41, 15))

    state.addChoice(RED, 'orange',
                    Tank((39, 19), RED, 'rTank1', HIDDEN),
                    Infantry((34, 15), RED, 'rInf11', HIDDEN)
                    )
    state.addChoice(RED, 'red',
                    Tank((37, 18), RED, 'rTank2', HIDDEN),
                    Infantry((33, 14), RED, 'rInf12', HIDDEN)
                    )
    state.addChoice(RED, 'darkred',
                    Tank((35, 16), RED, 'rTank3', HIDDEN),
                    Infantry((32, 13), RED, 'rInf21', HIDDEN)
                    )

    state.addFigure(
        APC((40, 11), BLUE, 'bAPC', HIDDEN),
        Infantry((42, 9), BLUE, 'bInf', HIDDEN),
    )

    placement_zone_red = np.zeros(shape, dtype='uint8')
    placement_zone_red[28, 11:24] = 1
    placement_zone_red[29, 12:24] = 1
    placement_zone_red[30, 12:24] = 1
    placement_zone_red[31, 13:24] = 1
    placement_zone_red[32, 13:24] = 1
    placement_zone_red[33, 14:24] = 1
    placement_zone_red[34, 14:24] = 1
    placement_zone_red[35, 15:24] = 1
    placement_zone_red[36, 15:24] = 1
    placement_zone_red[37, 17:24] = 1
    placement_zone_red[38, 17:24] = 1
    placement_zone_red[39, 18:24] = 1
    placement_zone_red[40, 18:24] = 1
    placement_zone_red[41, 19:24] = 1
    placement_zone_red[42, 19:24] = 1
    placement_zone_red[43, 20:23] = 1
    placement_zone_red[44, 19:22] = 1
    placement_zone_red[45, 21:22] = 1
    placement_zone_red[46, 20:21] = 1
    placement_zone_red[47, 21] = 1

    placement_zone_blue = np.zeros(shape, dtype='uint8')
    placement_zone_blue[44, 3:15] = 1
    placement_zone_blue[43, 4:15] = 1
    placement_zone_blue[42, 4:16] = 1
    placement_zone_blue[41, 5:17] = 1
    placement_zone_blue[40, 5:17] = 1
    placement_zone_blue[39, 6:17] = 1
    placement_zone_blue[38, 6:15] = 1
    placement_zone_blue[37, 7:14] = 1
    placement_zone_blue[36, 7:12] = 1
    placement_zone_blue[35, 8:11] = 1
    placement_zone_blue[34, 8:10] = 1
    placement_zone_blue[33, 9] = 1

    board.addPlacementZone(RED, placement_zone_red)
    board.addPlacementZone(BLUE, placement_zone_blue)

    board.name = state.name = 'bridgehead'

    return board, state


def scenarioCrossingTheCity() -> (GameBoard, GameState):
    """
    Sets up scenario 'CrossingTheCity'.
    """
    board = GameBoard(shape)
    state = GameState(shape)
    state.turn_max = 6

    # setup static parameters
    # TODO: raise height of shape!
    # better TODO: use complete map
    terrain = np.zeros(shape, dtype='uint8')
    basicForest(terrain)
    basicUrban(terrain)
    basicRoad(terrain)

    terrain[25, 3:6] = Terrain.FOREST
    terrain[26, 2:5] = Terrain.FOREST
    terrain[27, 4:5] = Terrain.FOREST
    terrain[28, 3:4] = Terrain.FOREST
    terrain[29, 3:4] = Terrain.FOREST
    terrain[30, 1:3] = Terrain.FOREST
    terrain[31, 2] = Terrain.FOREST

    board.setObjectives((30, 9))

    t1 = Tank((29, 2), RED, 'rTank2')  # orange
    i11 = Infantry((29, 2), RED, 'rInf21')
    i12 = Infantry((29, 2), RED, 'rInf21')
    t1.transportLoad(i11)
    t1.transportLoad(i12)

    t2 = Tank((24, 4), RED, 'rTank3')  # red 1 unit
    i21 = Infantry((24, 4), RED, 'rInf31')
    i22 = Infantry((24, 4), RED, 'rInf31')
    t2.transportLoad(i21)
    t2.transportLoad(i22)

    t3 = Tank((29, 1), RED, 'rTank1')  # dark red 2 units
    i31 = Infantry((29, 1), RED, 'rInf11')
    i32 = Infantry((29, 1), RED, 'rInf11')
    t3.transportLoad(i31)
    t3.transportLoad(i32)

    state.addChoice(RED, 'orange', t1, i11, i12)
    state.addChoice(RED, 'red', t2, i21, i22)
    state.addChoice(RED, 'darkred', t3, i31, i32)

    state.addFigure(
        APC((32, 7), BLUE, 'bAPC', HIDDEN),
        Infantry((31, 9), BLUE, 'bInf', HIDDEN),
    )

    placement_zone_blue = np.zeros(shape, dtype='uint8')
    placement_zone_blue[26, 6:8] = Terrain.FOREST
    placement_zone_blue[26, 1:9] = Terrain.FOREST
    placement_zone_blue[26, 0:8] = Terrain.FOREST
    placement_zone_blue[26, 0:9] = Terrain.FOREST
    placement_zone_blue[26, 0:8] = Terrain.FOREST
    placement_zone_blue[26, 0:9] = Terrain.FOREST
    placement_zone_blue[26, 0:8] = Terrain.FOREST
    placement_zone_blue[26, 0:9] = Terrain.FOREST
    placement_zone_blue[26, 0:8] = Terrain.FOREST
    placement_zone_blue[26, 0:9] = Terrain.FOREST
    placement_zone_blue[26, 0:8] = Terrain.FOREST
    placement_zone_blue[26, 0:9] = Terrain.FOREST

    board.addPlacementZone(BLUE, placement_zone_blue)

    board.name = state.name = 'crossingthecity'

    return board, state
