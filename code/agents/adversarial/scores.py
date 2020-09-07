import numpy as np

from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube, cube_distance, cube_to_hex


def evaluateBoard(board: GameBoard, team):
    """Distributes values over the board based on team's objectives."""
    boardValues = np.zeros(board.shape)
    objs = board.getObjectivesPositions(team)

    for x, y in np.ndindex(board.shape):
        xy = to_cube((x, y))
        for o in objs:
            boardValues[x, y] = cube_distance(xy, o)

    maxBV = np.max(boardValues)

    for x, y in np.ndindex(board.shape):
        boardValues[x, y] = 1 - boardValues[x, y] / maxBV

    for o in objs:
        boardValues[cube_to_hex(o)] = 5

    return boardValues


def evaluateState(boardValues: np.ndarray, state: GameState) -> float:
    """Assign a score to the given status, based on the board."""
    value: float = 0.0

    for figure in state.getFigures(RED):
        if not figure.killed:
            value += 0.2 * boardValues[cube_to_hex(figure.position)] + 1

    for figure in state.getFigures(BLUE):
        if not figure.killed:
            value += 0.2 * boardValues[cube_to_hex(figure.position)] + 1

    # if state.turn >= self.board['totalTurns']: TODO: add penalty to endgame
    #     return -5

    return value
