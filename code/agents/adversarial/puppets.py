from agents import Agent
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState


class Puppet(Agent):
    """This is just a "puppet", a fake-agent that answer always with the same action/response, that can be changed."""

    def __init__(self, team: str):
        super().__init__('puppet', team)

        self.action: Action or None = None
        self.response: Action or None = None

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        return self.action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        return self.response
