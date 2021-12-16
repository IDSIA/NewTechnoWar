import logging
from typing import Tuple

import numpy as np

from agents import Agent, GreedyAgent
from agents.reinforced import MCTS, ModelWrapper
from agents.reinforced.utils import ACT, RES
from core.actions import Action, NoResponse, Wait
from core.const import BLUE, RED
from core.game import GameBoard, GameState

logger = logging.getLogger(__name__)


class MCTSAgent(Agent):

    def __init__(self, team: str, shape: Tuple[int, int], checkpoint: str = '.', seed: int = 0, max_unit_per_team: int = 4,
                 num_MCTS_sims: int = 30, cpuct: float = 1, max_depth: int = 100, name: str = 'MCTSAgent'
                 ):
        super().__init__(name, team, seed=seed)

        self.RED = ModelWrapper(shape, seed, max_units_per_team=max_unit_per_team)
        self.BLUE = ModelWrapper(shape, seed, max_units_per_team=max_unit_per_team)

        self.RED.load_checkpoint(checkpoint, f'model_{RED}.pth.tar')
        self.BLUE.load_checkpoint(checkpoint, f'model_{BLUE}.pth.tar')

        self.mcts = MCTS(shape, self.RED, self.BLUE, seed, num_MCTS_sims, cpuct, max_depth, max_unit_per_team)

    def predict(self, board: GameBoard, state: GameState, action_type):
        valid_indices, valid_actions = self.mcts.actionIndexMapping(board, state, self.team, action_type)
        actions = valid_actions[valid_indices]

        pi, _ = self.mcts.getActionProb(board, state, self.team, action_type)

        pi: np.ndarray = pi[valid_indices]
        pi /= pi.sum()

        if max(pi) == 1:
            logger.debug(f'Unexpected single choice! Index: {np.argmax(pi)}')

        # choose next action and load in correct puppet
        action = self.random.choice(actions, p=pi)

        return action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        a = self.predict(board, state, ACT)
        return a if a else Wait(self.team)

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        r = self.predict(board, state, RES)
        return r if r else NoResponse(self.team)

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
