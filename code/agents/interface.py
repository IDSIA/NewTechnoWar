from datetime import datetime

import pandas as pd

from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState


class Agent:

    def __init__(self, name: str, team: str, seed: int = 0):
        self.name: str = name
        self.team: str = team
        self.seed: int = seed
        self.count: int = 0

        self.history: list = []

    def register(self, data: list):
        self.count += 1
        self.history.append([datetime.now(), self.team, self.seed, self.count] + data)

    def dataFrameInfo(self):
        return [
            "time",
            "team",
            "seed",
            "count",
        ]

    def createDataFrame(self):
        return pd.DataFrame(data=self.history, columns=self.dataFrameInfo())

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
