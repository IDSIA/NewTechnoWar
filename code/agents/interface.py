from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState


class Agent:

    def __init__(self, name: str, team: str):
        self.name = name
        self.team = team

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        raise NotImplemented()

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        raise NotImplemented()

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        raise NotImplemented()

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        raise NotImplemented()
