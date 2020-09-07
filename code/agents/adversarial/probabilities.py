from core import GM
from core.const import RED, BLUE
from core.actions import Attack, Move
from core.game.board import GameBoard
from core.game.state import GameState


def probabilityOfSuccessfulAttack(board: GameBoard, state: GameState, action: Attack) -> float:
    _, outcome = GM.activate(board, state, action)
    return outcome['hitScore'] / 20.0


def probabilityOfSuccessfulResponseAccumulated(board: GameBoard, state: GameState, action: Attack or Move) -> float:
    prob = 0.0
    _r = 1.0

    if isinstance(action, Move):
        team = RED if action.team == BLUE else BLUE

        for figure in state.getFiguresCanRespond(team):
            for response in GM.buildResponses(board, state, figure, action):
                _r *= (1 - probabilityOfSuccessfulAttack(board, state, response))

        prob = 1 - _r

    if isinstance(action, Attack):
        prob = probabilityOfSuccessfulAttack(board, state, action)

    return prob
