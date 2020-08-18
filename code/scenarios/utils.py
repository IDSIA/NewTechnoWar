import numpy as np

from core.game.board import GameBoard
from core.game.state import GameState
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
