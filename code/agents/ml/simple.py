import logging
import os
from typing import List, Tuple

import joblib
import numpy as np

from agents import Agent, GreedyAgent
from agents.utils import entropy, standardD
from core.actions import Action
from core.game import GameBoard, GameState

logger = logging.getLogger(__name__)

# NOTE: deprecated, see agents.ml.__init__.py file


class MLAgent(Agent):

    def __init__(self, name: str, team: str, filename: str, randomChoice: bool = False, tops: int = 10, seed: int = 0):
        """
        :param name:            name of this agent
        :param team:            color of the team
        :param filename:        path to the model file stored on disk
        :param randomChoice:    if true, in case of same score the action is chosen randomly
        :param tops:            if randomChoice is true, this defines the pool of top N actions to chose from
        :param seed:            random seed to use internally
        """
        super().__init__(name, team, seed)

        self.filename: str = filename
        self.model = joblib.load(os.path.join(os.getcwd(), filename))

        self.randomChoice: bool = randomChoice
        self.tops: int = tops

    def dataFrameInfo(self) -> List[str]:
        """
        The additional columns are:
            - score:            score associated with the chosen action
            - action:           action performed
            - entropy:          entropy valued associated with the chosen action
            - n_scores:         number of available actions
            - scores:           scores for all the available actions
            - actions:          all the available actions
            - random_choice:    value of parameter randomChoice
            - n_choices:        number of available choices

        :return: a list with the name of the columns used in the dataframe
        """
        return super().dataFrameInfo() + [
            'score', 'action', 'entropy', 'standard_deviation', 'n_scores', 'scores',
            'actions']  # ,'random_choice','n_choices']

    def store(self, state: GameState, bestScore: float, bestAction: Action,
              scoreActions: List[Tuple[float, Action]]) -> None:
        """
        Wrapper of the register() method that does some pre-processing on the data that will be saved.

        :param state:           state of the game
        :param bestScore:       score of the best action found
        :param bestAction:      best action found
        :param scoreActions:    list of all actions with their score
        """
        scores = [i[0] for i in scoreActions]
        actions = [type(i[1]).__name__ for i in scoreActions]

        h = entropy(scores)
        std = standardD(scores)

        eps = np.finfo(np.float32).eps

        # if h > 1. + 0.7 or h < 0. - eps:
        #     logger.warning(f'Entropy out of range: {h}')
        #     logger.warning(f'{scores}')

        data = [bestScore, type(bestAction).__name__, h, std, len(scores), scores,
                actions]  # , self.randomChoice, self.tops]

        self.register(state, data)

    def scores(self, board: GameBoard, state: GameState, actions: List[Action]) -> List[Tuple[float, Action]]:
        """
        This is the basic method to implement in order to have the ML-based agents to work. The model should take as
        input at least the stateActions list and assign a score for each one of them.

        The ideal implementation takes the X vector defined as following:

            X = [vectorState(state) + vectorAction(action) + vectorBoard(board, state, action) for action in actions]

        Then converts it in a Pandas DataFrame:

            df = pd.DataFrame(data=X, columns=vectorStateInfo() + vectorActionInfo() + vectorBoardInfo()).dropna(axis=1)
            df = df.drop(['meta_seed', 'meta_scenario', 'action_team'], axis=1)

        And finally perform the prediction:

                scores = self.model.predict_proba(df)

        Add pre- and post-processing as required.

        :param board:       board of the game
        :param state:       state of the game
        :param actions:     list of available actions to score
        :return: list of all actions with their score
        """
        raise NotImplemented()

    @staticmethod
    def bestAction(scores: List[Tuple[float, Action]]):
        """
        Iter ofer all the given scores and find the action with the maximum (always considered the best) score.

        :param scores:  list of all actions with their score
        :return: the best action with the associated score
        """
        bestScore, bestAction = -1e9, None
        for score, action in scores:
            if score >= bestScore:
                bestScore, bestAction = score, action

        return bestScore, bestAction

    def bestActionRandom(self, scores: List[Tuple[float, Action]]) -> Tuple[float, Action]:
        """
        Sort the given list of scores and take one randomly between the best N actions, where N is defined by the top .

        :param scores:  list of all actions with their score
        :return: the next action found with its score
        """
        bestScore, bestAction = 0.0, None
        if len(scores) > 0:
            sorted_multi_list = sorted(scores, key=lambda x: x[0])
            choice = self.random.integers(0, min(self.tops, len(scores)))
            bestScore, bestAction = sorted_multi_list[:self.tops][choice]
        return bestScore, bestAction

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        """
        Use the internal ML model to find the best next action to apply. If the randomChoice parameter is true, then it
        finds a random action between the best tops actions.

        :param board:   board of the game
        :param state:   the current state
        :return: the next action to apply
        """
        all_actions = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [self.gm.actionPassFigure(figure)] + \
                self.gm.buildAttacks(board, state, figure) + \
                self.gm.buildMovements(board, state, figure)

            all_actions += actions

        if not all_actions:
            logger.warning('No actions available: no action given')
            raise ValueError('No action given')

        scores = self.scores(board, state, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        self.store(state, bestScore, bestAction, scores)

        if not bestAction:
            logger.warning('No best action found: no action given')
            raise ValueError('No action given')

        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        """
        Use the internal ML model to find the best next response to apply. If the randomChoice parameter is true, then
        it finds a random action between the best topn actions.

        :param board:   board of the game
        :param state:   the current state
        :return: the next response to apply
        """
        all_actions = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [self.gm.actionNoResponse(self.team)] + \
                self.gm.buildResponses(board, state, figure)

            all_actions += actions

        if not all_actions:
            logger.warning('No actions available: no response given')
            raise ValueError('No response given')

        scores = self.scores(board, state, all_actions)

        if self.randomChoice:
            bestScore, bestAction = self.bestActionRandom(scores)
        else:
            bestScore, bestAction = self.bestAction(scores)

        if not bestAction:
            logger.warning('No best action found: no response given')
            raise ValueError('No response given')

        self.store(state, bestScore, bestAction, scores)

        logger.debug(f'BEST RESPONSE {self.team:5}: {bestAction} ({bestScore})')

        return bestAction

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """
        Uses the placeFigures() method of the GreedyAgent class.

        :param board:   board of the game
        :param state:   the current state
        """
        # TODO: find a better idea?
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        """
        Chooses randomly the initial color to use.

        :param board:   board of the game
        :param state:   the current state
        """
        # TODO: find a better idea? now random
        colors = list(state.choices[self.team].keys())
        color = self.random.choice(colors)

        state.choose(self.team, color)
