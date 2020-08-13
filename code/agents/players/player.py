from core.actions import Action
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState


class Player:

    def __init__(self, name: str, team: str):
        self.name = name
        self.team = team

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        raise NotImplemented()

    def chooseResponse(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        raise NotImplemented()
