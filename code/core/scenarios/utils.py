import numpy as np

from core.game import GameBoard, GameState
from core.utils.coordinates import Hex


def blank(shape) -> (GameBoard, GameState):
    return GameBoard(shape), GameState(shape)


def parse_slice(value: str) -> slice:
    """
    Parses a `slice()` from string, like `start:stop:step`.
    """
    value = value.strip()
    if value:
        if ':' in value:
            parts = value.split(':')
            if len(parts) == 1:
                # slice(stop)
                parts = [None, parts[0]]
            # else: slice(start, stop[, step])
        else:
            parts = [int(value), int(value) + 1]
    else:
        # slice()
        parts = []
    return slice(*[int(p) if p else None for p in parts])


def fillLine(terrain: np.ndarray, start: tuple, end: tuple, kind: int):
    if start[0] == end[0]:
        line = [Hex(start[0], j).cube() for j in range(start[1], end[1] + 1)]
    elif start[1] == end[1]:
        line = [Hex(i, start[1]).cube() for i in range(start[0], end[0] + 1)]
    else:
        line = Hex(t=start).line(Hex(t=end))
    for hex in line:
        terrain[hex.tuple()] = kind
