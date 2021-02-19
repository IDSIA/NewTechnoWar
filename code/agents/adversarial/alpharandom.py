import numpy as np

from agents import Agent, AlphaBetaAgent
from core.actions import Action, PassTeam, PassFigure
from core.game import GM, GameBoard, GameState
from core.utils.coordinates import to_cube

ACTION_MOVE = 0
ACTION_ATTACK = 1
ACTION_PASS = 2


class AlphaRandomAgent(AlphaBetaAgent):

    def __init__(self, team: str):
        super().__init__(team,3)
        self.name = 'AlphaRandomAgent'

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        colors = list(state.choices[self.team].keys())
        color = np.random.choice(colors)

        state.choose(self.team, color)
