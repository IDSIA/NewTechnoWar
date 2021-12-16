from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

from core.actions import Action
from core.game import GameBoard, GameState, GameManager


class Agent:
    """
    Agent basic interface class.
    """

    def __init__(self, name: str, team: str, seed: int = 0):
        """
        :param name:    name of this agent
        :param team:    color of the team
        :param seed:    random seed to use internally
        """
        self.name: str = name
        self.team: str = team
        self.seed: int = seed
        self.count: int = 0
        self.random = np.random.default_rng(seed)

        # history of registered actions used to build the dataframe of actions performed
        self.history: list = []

        # internal game manager
        self.gm: GameManager = GameManager(seed)

    def register(self, state: GameState, data: list) -> None:
        """
        Register the current state in the history of the agent.

        :param state:   state to register
        :param data:    additional data to be registered
        """
        self.count += 1
        self.history.append([datetime.now(), self.team, self.seed, self.count] + data)

    def dataFrameInfo(self) -> List[str]:
        """
        If you need more column, since you want to save more "data", override this method and add the column names at
        the end of this list.

        The default column values are:
            - time:     when the event happened
            - team:     the color of the agent's team
            - seed:     the seed value used
            - turn:     in which turn the action happened
            - count:    internal index that count the number of actions performed

        :return: a list with the name of the columns used in the dataframe
        """
        return [
            "time",
            "team",
            "seed",
            # "turn",
            "count",
        ]

    def createDataFrame(self) -> pd.DataFrame:
        """
        :return: a Pandas DataFrame composed by the history of actions performed
        """
        return pd.DataFrame(data=self.history, columns=self.dataFrameInfo())

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        """
        The implementation of this method should return the chosen action to apply to the given state.

        :param board:   board of the game
        :param state:   the current state
        :return: the next action to apply
        """
        raise NotImplemented()

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        """
        The implementation of this method should return the chosen response to apply to the given state.

        :param board:   board of the game
        :param state:   the current state
        :return: the next response to apply
        """
        raise NotImplemented()

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """
        If the scenario offers this possibility, in this method an agent can choose where to place its figures.

        This method should use the moveFigure() method of the given GameState object to move around the figures of the
        agent's team. You can move them around freely in the placement stage (before the first update).

        :param board:   board of the game
        :param state:   the current state
        """
        raise NotImplemented()

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        """
        If the scenario offers this possibility, in this method an agent can choose which group of figures to use.

        Once the agent chose a group, this method should use the choose() method of the given GameState object to choose
        which color to use. This can be done freely in the placement stage (before the first update).

        :param board:   board of the game
        :param state:   the current state
        """
        raise NotImplemented()
