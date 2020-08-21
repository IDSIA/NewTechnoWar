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


def basicForest(terrain: np.array):
    """
    Basic forest cover for default map.
    Source: main project source code.
    """

    # forest bottom right
    terrain[51, 2:].fill(Terrain.FOREST)
    terrain[50, 1:].fill(Terrain.FOREST)
    terrain[49, 2:].fill(Terrain.FOREST)
    terrain[49, 0] = Terrain.OPEN_GROUND
    terrain[49, 5:10].fill(Terrain.OPEN_GROUND)
    terrain[49, 13:18].fill(Terrain.OPEN_GROUND)
    terrain[48, -7:].fill(Terrain.FOREST)
    terrain[47, -5:].fill(Terrain.FOREST)
    terrain[46, -5:].fill(Terrain.FOREST)
    terrain[45, -4:].fill(Terrain.FOREST)
    terrain[44, -4:-1].fill(Terrain.FOREST)

    # forest bottom middle
    terrain[35, -2:].fill(Terrain.FOREST)
    terrain[34, -3:].fill(Terrain.FOREST)
    terrain[33, -3:].fill(Terrain.FOREST)
    terrain[32, -4:].fill(Terrain.FOREST)
    terrain[31, -4:].fill(Terrain.FOREST)
    terrain[30, -5:].fill(Terrain.FOREST)
    terrain[29, -4:].fill(Terrain.FOREST)
    terrain[28, -5:].fill(Terrain.FOREST)
    terrain[27, -5:].fill(Terrain.FOREST)
    terrain[26, -5:].fill(Terrain.FOREST)
    terrain[25, -3:].fill(Terrain.FOREST)

    # forest bottom left
    terrain[0, -6:].fill(Terrain.FOREST)
    terrain[1, -6:].fill(Terrain.FOREST)
    terrain[2, -6:].fill(Terrain.FOREST)
    terrain[3, -6:].fill(Terrain.FOREST)
    terrain[4, -6:].fill(Terrain.FOREST)
    terrain[5, -6:].fill(Terrain.FOREST)
    terrain[6, -6:].fill(Terrain.FOREST)
    terrain[7, -6:].fill(Terrain.FOREST)
    terrain[8, -6:].fill(Terrain.FOREST)
    terrain[9, -7:].fill(Terrain.FOREST)
    terrain[10, -8:].fill(Terrain.FOREST)
    terrain[11, -9:].fill(Terrain.FOREST)
    terrain[12, -10:].fill(Terrain.FOREST)
    terrain[13, -9:].fill(Terrain.FOREST)
    terrain[14, -10:].fill(Terrain.FOREST)
    terrain[15, -9:-2].fill(Terrain.FOREST)
    terrain[16, -9:-5].fill(Terrain.FOREST)
    terrain[17, -8:-5].fill(Terrain.FOREST)
    terrain[18, -7:-6].fill(Terrain.FOREST)

    # forest up left
    terrain[0, 1:14].fill(Terrain.FOREST)
    terrain[1, 2:15].fill(Terrain.FOREST)
    terrain[2, 1:14].fill(Terrain.FOREST)
    terrain[3, 2:15].fill(Terrain.FOREST)
    terrain[4, 1:14].fill(Terrain.FOREST)
    terrain[5, 2:14].fill(Terrain.FOREST)
    terrain[6, 1:13].fill(Terrain.FOREST)
    terrain[7, 2:12].fill(Terrain.FOREST)
    terrain[8, 1:10].fill(Terrain.FOREST)


def basicUrban(terrain: np.array):
    """
    Basic urban cover for default map.
    Source: main project source code.
    """

    terrain[-20, 3:9].fill(Terrain.URBAN)
    terrain[-19, 2:10].fill(Terrain.URBAN)
    terrain[-18, 1:17].fill(Terrain.URBAN)
    terrain[-18, 9:14].fill(Terrain.OPEN_GROUND)
    terrain[-17, 2:18].fill(Terrain.URBAN)
    terrain[-17, 9:14].fill(Terrain.OPEN_GROUND)
    terrain[-16, 1:17].fill(Terrain.URBAN)
    terrain[-16, 8:13].fill(Terrain.OPEN_GROUND)
    terrain[-15, 2:19].fill(Terrain.URBAN)
    terrain[-15, 9:12].fill(Terrain.OPEN_GROUND)
    terrain[-14, 2:18].fill(Terrain.URBAN)
    terrain[-13, 3:19].fill(Terrain.URBAN)
    terrain[-12, 2:19].fill(Terrain.URBAN)
    terrain[-12, 3:19].fill(Terrain.URBAN)
    terrain[-11, 2:19].fill(Terrain.URBAN)
    terrain[-10, 2:19].fill(Terrain.URBAN)
    terrain[-9, 1:20].fill(Terrain.URBAN)
    terrain[-8, 3:20].fill(Terrain.URBAN)
    terrain[-7, 3:20].fill(Terrain.URBAN)
    terrain[-6, 3:20].fill(Terrain.URBAN)
    terrain[-5, 4:20].fill(Terrain.URBAN)
    terrain[-4, 4:18].fill(Terrain.URBAN)


def basicRoad(terrain: np.array):
    """
    Basic roads cover for default map.
    Source: main project source code.
    """

    terrain[::2, 0].fill(Terrain.ROAD)
    terrain[1::2, 1].fill(Terrain.ROAD)
    terrain[30, 0:17].fill(Terrain.ROAD)
    terrain[31, 17] = Terrain.ROAD
    terrain[32, 17] = Terrain.ROAD
    terrain[33, 18] = Terrain.ROAD
    terrain[34, 18] = Terrain.ROAD
    terrain[35, 19] = Terrain.ROAD
    terrain[36, 19] = Terrain.ROAD
    terrain[37, 20] = Terrain.ROAD
    terrain[38, 20] = Terrain.ROAD
    terrain[39, 21] = Terrain.ROAD
    terrain[40, 21] = Terrain.ROAD
    terrain[41, 22] = Terrain.ROAD
    terrain[42, 22] = Terrain.ROAD
    terrain[43, 23] = Terrain.ROAD
    terrain[44, 23] = Terrain.ROAD
    terrain[45, 24] = Terrain.ROAD

    terrain[30, 13] = Terrain.ROAD
    terrain[29, 14] = Terrain.ROAD
    terrain[28, 14] = Terrain.ROAD
    terrain[27, 15] = Terrain.ROAD
    terrain[26, 15] = Terrain.ROAD
    terrain[25, 16] = Terrain.ROAD
    terrain[24, 16] = Terrain.ROAD
    terrain[23, 17] = Terrain.ROAD
    terrain[22, 17] = Terrain.ROAD
    terrain[21, 18] = Terrain.ROAD
    terrain[20, 18] = Terrain.ROAD
    terrain[19, 19] = Terrain.ROAD
    terrain[18, 19] = Terrain.ROAD
    terrain[17, 20] = Terrain.ROAD
    terrain[17, 21] = Terrain.ROAD
    terrain[16, 21] = Terrain.ROAD
    terrain[16, 22] = Terrain.ROAD
    terrain[15, 23] = Terrain.ROAD
    terrain[15, 24] = Terrain.ROAD
