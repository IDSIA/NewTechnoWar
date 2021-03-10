from datetime import datetime

import pandas as pd

from core.actions import Action
from core.game import GameBoard, GameState, GameManager


class Agent:

    def __init__(self, name: str, team: str, seed: int = 0):
        self.name: str = name
        self.team: str = team
        self.seed: int = seed
        self.count: int = 0

        self.history: list = []

        self.gm: GameManager = GameManager()

    def register(self, state: GameState, data: list):
        self.count += 1
        self.history.append([datetime.now(), self.team, self.seed, self.count] + data)

    def dataFrameInfo(self):
        return [
            "time",
            "team",
            "seed",
            #"turn",
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
