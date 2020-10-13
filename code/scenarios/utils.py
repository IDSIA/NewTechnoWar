import numpy as np

from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import Terrain
from utils.coordinates import hex_linedraw, to_hex

MAP_SHAPE = (52, 42)  # entire map: 52x42


def blank(shape) -> (GameBoard, GameState):
    return GameBoard(shape), GameState(shape)


def parse_slice(value: str) -> slice:
    """
    Parses a `slice()` from string, like `start:stop:step`.
    """
    value = value.strip()
    if value:
        parts = value.split(':')
        if len(parts) == 1:
            # slice(stop)
            parts = [None, parts[0]]
        # else: slice(start, stop[, step])
    else:
        # slice()
        parts = []
    return slice(*[int(p) if p else None for p in parts])


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

    # forest top left
    terrain[:32, :3] = Terrain.FOREST
    terrain[:30, 3] = Terrain.FOREST
    terrain[:27, 4] = Terrain.FOREST
    terrain[:26, 5] = Terrain.FOREST
    terrain[:22, 6] = Terrain.FOREST
    terrain[23, 6] = Terrain.FOREST
    terrain[:21, 7] = Terrain.FOREST
    terrain[:20, 8] = Terrain.FOREST
    terrain[:18, 9] = Terrain.FOREST
    terrain[:16, 10] = Terrain.FOREST
    terrain[:14, 11] = Terrain.FOREST
    terrain[:10, 12] = Terrain.FOREST
    terrain[:8, 13:18] = Terrain.FOREST

    # forest middle left
    terrain[:8, 18:29] = Terrain.FOREST
    terrain[8, 18:27] = Terrain.FOREST
    terrain[:7, 29] = Terrain.FOREST
    terrain[:6, 30] = Terrain.FOREST
    terrain[1, 31] = Terrain.FOREST
    terrain[3, 31] = Terrain.FOREST

    # forest bottom right
    terrain[51, 19:] = Terrain.FOREST
    terrain[50, 18:] = Terrain.FOREST
    terrain[49, 19:22] = Terrain.FOREST
    terrain[49, 27:30] = Terrain.FOREST
    terrain[49, 35:] = Terrain.FOREST
    terrain[48, 35:] = Terrain.FOREST
    terrain[47, 37:] = Terrain.FOREST
    terrain[46, 37:] = Terrain.FOREST
    terrain[45, 38:] = Terrain.FOREST
    terrain[44, 38:41] = Terrain.FOREST

    # forest bottom middle
    terrain[35, -2:] = Terrain.FOREST
    terrain[34, -3:] = Terrain.FOREST
    terrain[33, -3:] = Terrain.FOREST
    terrain[32, -4:] = Terrain.FOREST
    terrain[31, -4:] = Terrain.FOREST
    terrain[30, -5:] = Terrain.FOREST
    terrain[29, -4:] = Terrain.FOREST
    terrain[28, -5:] = Terrain.FOREST
    terrain[27, -5:] = Terrain.FOREST
    terrain[26, -5:] = Terrain.FOREST
    terrain[25, -3:] = Terrain.FOREST

    # forest bottom left
    terrain[0, -6:] = Terrain.FOREST
    terrain[1, -6:] = Terrain.FOREST
    terrain[2, -6:] = Terrain.FOREST
    terrain[3, -6:] = Terrain.FOREST
    terrain[4, -6:] = Terrain.FOREST
    terrain[5, -6:] = Terrain.FOREST
    terrain[6, -6:] = Terrain.FOREST
    terrain[7, -6:] = Terrain.FOREST
    terrain[8, -6:] = Terrain.FOREST
    terrain[9, -7:] = Terrain.FOREST
    terrain[10, -8:] = Terrain.FOREST
    terrain[11, -8:] = Terrain.FOREST
    terrain[12, -10:] = Terrain.FOREST
    terrain[13, -9:] = Terrain.FOREST
    terrain[14, -10:] = Terrain.FOREST
    terrain[15, -9:-2] = Terrain.FOREST
    terrain[16, -9:-5] = Terrain.FOREST
    terrain[17, -8:-5] = Terrain.FOREST
    terrain[18, -7:-6] = Terrain.FOREST


def basicUrban(terrain: np.array):
    """
    Basic CONCRETE_BUILDING cover for default map.
    Source: main project source code.
    """

    # city
    terrain[-20, 20:26] = Terrain.CONCRETE_BUILDING
    terrain[-19, 19:27] = Terrain.CONCRETE_BUILDING
    terrain[-18, 18:34] = Terrain.CONCRETE_BUILDING
    terrain[-18, 26:31] = Terrain.OPEN_GROUND
    terrain[-17, 19:35] = Terrain.CONCRETE_BUILDING
    terrain[-17, 26:31] = Terrain.OPEN_GROUND
    terrain[-16, 18:34] = Terrain.CONCRETE_BUILDING
    terrain[-16, 25:30] = Terrain.OPEN_GROUND
    terrain[-15, 19:36] = Terrain.CONCRETE_BUILDING
    terrain[-15, 26:30] = Terrain.OPEN_GROUND
    terrain[-14, 19:35] = Terrain.CONCRETE_BUILDING
    terrain[-13, 20:36] = Terrain.CONCRETE_BUILDING
    terrain[-12, 19:36] = Terrain.CONCRETE_BUILDING
    terrain[-12, 20:36] = Terrain.CONCRETE_BUILDING
    terrain[-11, 19:36] = Terrain.CONCRETE_BUILDING
    terrain[-10, 19:36] = Terrain.CONCRETE_BUILDING
    terrain[-9, 18:37] = Terrain.CONCRETE_BUILDING
    terrain[-8, 20:37] = Terrain.CONCRETE_BUILDING
    terrain[-7, 20:37] = Terrain.CONCRETE_BUILDING
    terrain[-6, 20:37] = Terrain.CONCRETE_BUILDING
    terrain[-5, 21:37] = Terrain.CONCRETE_BUILDING
    terrain[-4, 21:35] = Terrain.CONCRETE_BUILDING

    # village
    terrain[15, 29:31] = Terrain.WOODEN_BUILDING
    terrain[16, 29:31] = Terrain.WOODEN_BUILDING
    terrain[17, 30:32] = Terrain.WOODEN_BUILDING


def basicRoad(terrain: np.array):
    """
    Basic roads cover for default map.
    Source: main project source code.
    """

    # main road
    for i in range(MAP_SHAPE[0]):
        j = 17 if i % 2 == 0 else 18
        terrain[i, j] = Terrain.ROAD

    # secondary roads
    terrain[30, 18:34] = Terrain.ROAD

    fillLine(terrain, (30, 33), (46, 41), Terrain.ROAD)
    fillLine(terrain, (30, 30), (17, 37), Terrain.ROAD)
    fillLine(terrain, (17, 37), (15, 41), Terrain.ROAD)
    fillLine(terrain, (20, 35), (18, 31), Terrain.ROAD)
    fillLine(terrain, (41, 36), (41, 39), Terrain.ROAD)

    # city roads
    fillLine(terrain, (31, 25), (38, 22), Terrain.ROAD)
    fillLine(terrain, (36, 21), (38, 22), Terrain.ROAD)
    fillLine(terrain, (39, 23), (42, 21), Terrain.ROAD)
    fillLine(terrain, (39, 23), (42, 26), Terrain.ROAD)
    fillLine(terrain, (42, 26), (45, 25), Terrain.ROAD)
    fillLine(terrain, (43, 26), (44, 30), Terrain.ROAD)
    fillLine(terrain, (41, 30), (41, 38), Terrain.ROAD)
    fillLine(terrain, (41, 32), (47, 30), Terrain.ROAD)

    terrain[40, 28:30] = Terrain.ROAD


def basicTerrain():
    terrain = np.zeros(MAP_SHAPE, dtype='uint8')
    basicUrban(terrain)
    basicForest(terrain)
    basicRoad(terrain)

    return terrain
