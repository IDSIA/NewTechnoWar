from agents import Agent
from core.actions import Action
from core.game import GameBoard, GameState


class Puppet(Agent):
    """This is just a "puppet", a fake-agent that answer always with the same action/response, that can be changed."""

    def __init__(self, team: str):
        super().__init__('puppet', team)

        # action to perform
        self.action: Action or None = None
        # response to perform
        self.response: Action or None = None

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        return self.action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        return self.response
