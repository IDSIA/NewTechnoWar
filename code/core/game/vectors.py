from core.game.board import GameBoard
from core.game.state import GameState


def vectorBoardInfo() -> tuple:
    # TODO: add header for features that are board-dependent
    raise NotImplemented()


def vectorBoard(board: GameBoard, state: GameState) -> tuple:
    # TODO: add features that are an interaction of board and state:
    #       - distance from goals
    #       - LOS/LOF blocked
    #       - distance to cover (forest, building)
    raise NotImplemented()
