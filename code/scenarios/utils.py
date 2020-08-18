import numpy as np

from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from utils.coordinates import hex_linedraw, to_hex


def blank(shape) -> (GameBoard, GameState):
    return GameBoard(shape), GameState(shape)


def fillLine(terrain: np.ndarray, start: tuple, end: tuple, kind: int):
    if start[0] == end[0]:
        line = [(start[0], j) for j in range(start[1], end[1] + 1)]
    elif start[1] == end[1]:
        line = [(i, start[1]) for i in range(start[0], end[0] + 1)]
    else:
        line = hex_linedraw(to_hex(start), to_hex(end))
    for hex in line:
        terrain[hex] = kind


def basicForest():
    """
    Basic forest cover for default map.
    Source: main project source code.
    """
    forest = np.zeros((52, 25), dtype='uint8')

    # forest bottom right
    forest[51, 2:].fill(Terrain.FOREST)
    forest[50, 1:].fill(Terrain.FOREST)
    forest[49, 2:].fill(Terrain.FOREST)
    forest[49, 0] = Terrain.OPEN_GROUND
    forest[49, 5:10].fill(Terrain.OPEN_GROUND)
    forest[49, 13:18].fill(Terrain.OPEN_GROUND)
    forest[48, -7:].fill(Terrain.FOREST)
    forest[47, -5:].fill(Terrain.FOREST)
    forest[46, -5:].fill(Terrain.FOREST)
    forest[45, -4:].fill(Terrain.FOREST)
    forest[44, -4:-1].fill(Terrain.FOREST)

    # forest bottom middle
    forest[35, -2:].fill(Terrain.FOREST)
    forest[34, -3:].fill(Terrain.FOREST)
    forest[33, -3:].fill(Terrain.FOREST)
    forest[32, -4:].fill(Terrain.FOREST)
    forest[31, -4:].fill(Terrain.FOREST)
    forest[30, -5:].fill(Terrain.FOREST)
    forest[29, -4:].fill(Terrain.FOREST)
    forest[28, -5:].fill(Terrain.FOREST)
    forest[27, -5:].fill(Terrain.FOREST)
    forest[26, -5:].fill(Terrain.FOREST)
    forest[25, -3:].fill(Terrain.FOREST)

    # forest bottom left
    forest[0, -6:].fill(Terrain.FOREST)
    forest[1, -6:].fill(Terrain.FOREST)
    forest[2, -6:].fill(Terrain.FOREST)
    forest[3, -6:].fill(Terrain.FOREST)
    forest[4, -6:].fill(Terrain.FOREST)
    forest[5, -6:].fill(Terrain.FOREST)
    forest[6, -6:].fill(Terrain.FOREST)
    forest[7, -6:].fill(Terrain.FOREST)
    forest[8, -6:].fill(Terrain.FOREST)
    forest[9, -7:].fill(Terrain.FOREST)
    forest[10, -8:].fill(Terrain.FOREST)
    forest[11, -9:].fill(Terrain.FOREST)
    forest[12, -10:].fill(Terrain.FOREST)
    forest[13, -9:].fill(Terrain.FOREST)
    forest[14, -10:].fill(Terrain.FOREST)
    forest[15, -9:-2].fill(Terrain.FOREST)
    forest[16, -9:-5].fill(Terrain.FOREST)
    forest[17, -8:-5].fill(Terrain.FOREST)
    forest[18, -7:-6].fill(Terrain.FOREST)

    # forest up left
    forest[0, 1:14].fill(Terrain.FOREST)
    forest[1, 2:15].fill(Terrain.FOREST)
    forest[2, 1:14].fill(Terrain.FOREST)
    forest[3, 2:15].fill(Terrain.FOREST)
    forest[4, 1:14].fill(Terrain.FOREST)
    forest[5, 2:14].fill(Terrain.FOREST)
    forest[6, 1:13].fill(Terrain.FOREST)
    forest[7, 2:12].fill(Terrain.FOREST)
    forest[8, 1:10].fill(Terrain.FOREST)

    return forest


def basicUrban():
    """
    Basic urban cover for default map.
    Source: main project source code.
    """

    city = np.zeros((52, 25), dtype='uint8')
    city[-20, 3:9].fill(Terrain.URBAN)
    city[-19, 2:10].fill(Terrain.URBAN)
    city[-18, 1:17].fill(Terrain.URBAN)
    city[-18, 9:14].fill(Terrain.OPEN_GROUND)
    city[-17, 2:18].fill(Terrain.URBAN)
    city[-17, 9:14].fill(Terrain.OPEN_GROUND)
    city[-16, 1:17].fill(Terrain.URBAN)
    city[-16, 8:13].fill(Terrain.OPEN_GROUND)
    city[-15, 2:19].fill(Terrain.URBAN)
    city[-15, 9:12].fill(Terrain.OPEN_GROUND)
    city[-14, 2:18].fill(Terrain.URBAN)
    city[-13, 3:19].fill(Terrain.URBAN)
    city[-12, 2:19].fill(Terrain.URBAN)
    city[-12, 3:19].fill(Terrain.URBAN)
    city[-11, 2:19].fill(Terrain.URBAN)
    city[-10, 2:19].fill(Terrain.URBAN)
    city[-9, 1:20].fill(Terrain.URBAN)
    city[-8, 3:20].fill(Terrain.URBAN)
    city[-7, 3:20].fill(Terrain.URBAN)
    city[-6, 3:20].fill(Terrain.URBAN)
    city[-5, 4:20].fill(Terrain.URBAN)
    city[-4, 4:18].fill(Terrain.URBAN)
    return city


def basicRoad():
    """
    Basic roads cover for default map.
    Source: main project source code.
    """

    roads = np.zeros((52, 25), dtype='uint8')
    roads[::2, 0].fill(Terrain.ROAD)
    roads[1::2, 1].fill(Terrain.ROAD)
    roads[30, 0:17].fill(Terrain.ROAD)
    roads[31, 17] = Terrain.ROAD
    roads[32, 17] = Terrain.ROAD
    roads[33, 18] = Terrain.ROAD
    roads[34, 18] = Terrain.ROAD
    roads[35, 19] = Terrain.ROAD
    roads[36, 19] = Terrain.ROAD
    roads[37, 20] = Terrain.ROAD
    roads[38, 20] = Terrain.ROAD
    roads[39, 21] = Terrain.ROAD
    roads[40, 21] = Terrain.ROAD
    roads[41, 22] = Terrain.ROAD
    roads[42, 22] = Terrain.ROAD
    roads[43, 23] = Terrain.ROAD
    roads[44, 23] = Terrain.ROAD
    roads[45, 24] = Terrain.ROAD

    roads[30, 13] = Terrain.ROAD
    roads[29, 14] = Terrain.ROAD
    roads[28, 14] = Terrain.ROAD
    roads[27, 15] = Terrain.ROAD
    roads[26, 15] = Terrain.ROAD
    roads[25, 16] = Terrain.ROAD
    roads[24, 16] = Terrain.ROAD
    roads[23, 17] = Terrain.ROAD
    roads[22, 17] = Terrain.ROAD
    roads[21, 18] = Terrain.ROAD
    roads[20, 18] = Terrain.ROAD
    roads[19, 19] = Terrain.ROAD
    roads[18, 19] = Terrain.ROAD
    roads[17, 20] = Terrain.ROAD
    roads[17, 21] = Terrain.ROAD
    roads[16, 21] = Terrain.ROAD
    roads[16, 22] = Terrain.ROAD
    roads[15, 23] = Terrain.ROAD
    roads[15, 24] = Terrain.ROAD

    return roads
