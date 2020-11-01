import numpy as np

from agents import Agent
from core import GM
from core.actions import Action, PassTeam, PassFigure
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube
from agents import AlphaBetaAgent

ACTION_MOVE = 0
ACTION_ATTACK = 1
ACTION_PASS = 2


class AlphaRandomAgent(AlphaBetaAgent):

    def __init__(self, team: str):
        super(AlphaRandomAgent, self).__init__(team,3)

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        # choose which figures that can still be activate will be activated
        return super(AlphaRandomAgent, self).chooseAction(board, state)

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        return super(AlphaRandomAgent, self).chooseResponse(board, state)

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        super(AlphaRandomAgent, self).placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        colors = list(state.choices[self.team].keys())
        color = np.random.choice(colors)

        state.choose(self.team, color)
