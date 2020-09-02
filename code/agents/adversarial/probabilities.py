from core import BLUE, RED
from core.actions import Attack, Move
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState


def probabilityOfSuccessfulAttack(gm: GameManager, board: GameBoard, state: GameState, action: Attack) -> float:
    _, outcome = gm.activate(board, state, action)
    return outcome['hitScore'] / 20.0


def probabilityOfSuccessfulResponseAccumulated(
        gm: GameManager, board: GameBoard, state: GameState, action: Attack or Move
) -> float:
    prob = 0.0
    _r = 1.0

    if isinstance(action, Move):
        team = RED if action.team == BLUE else BLUE

        for figure in state.getFiguresCanRespond(team):
            for response in gm.buildResponses(board, state, figure, action):
                _r *= (1 - probabilityOfSuccessfulAttack(gm, board, state, response))

        prob = 1 - _r

    if isinstance(action, Attack):
        prob = probabilityOfSuccessfulAttack(gm, board, state, action)

    return prob
