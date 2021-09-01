import logging

import numpy as np

from agents import Agent, GreedyAgent
from agents.reinforced import MCTS, ModelWrapper
from core.actions import Action, NoResponse, Wait
from core.game import GameBoard, GameState

logger = logging.getLogger(__name__)


class MCTSAgent(Agent):

    def __init__(self, team: str, board: GameBoard, checkpoint: str = '.', seed: int = 0, max_weapon_per_figure: int = 8, max_figure_per_scenario: int = 6,
                 max_move_no_response_size: int = 1351, max_attack_size: int = 288, num_MCTS_sims: int = 30, cpuct: float = 1
                 ):
        super().__init__('MCTSAgent', team, seed=seed)

        self.RED_Act = ModelWrapper(board.shape, seed)
        self.RED_Res = ModelWrapper(board.shape, seed)
        self.BLUE_Act = ModelWrapper(board.shape, seed)
        self.BLUE_Res = ModelWrapper(board.shape, seed)

        self.RED_Act.load_checkpoint(checkpoint, 'new_red_Act.pth.tar')
        self.RED_Res.load_checkpoint(checkpoint, 'new_red_Res.pth.tar')
        self.BLUE_Act.load_checkpoint(checkpoint, 'new_blue_Act.pth.tar')
        self.BLUE_Res.load_checkpoint(checkpoint, 'new_blue_Res.pth.tar')

        self.mcts = MCTS(self.RED_Act, self.RED_Res, self.BLUE_Act, self.BLUE_Res, seed, max_weapon_per_figure, max_figure_per_scenario,
                         max_move_no_response_size, max_attack_size, num_MCTS_sims, cpuct)

    def predict(self, board: GameBoard, state: GameState, action_type):
        _, valid_actions = self.mcts.actionIndexMapping(self.gm, board, state, self.team, action_type)

        pi, _ = self.mcts.getActionProb(board, state, self.team, action_type)

        if max(pi) == 1:
            action_index = np.argmax(pi)
            logger.debug(f'Unexpected single choice! Index: {action_index}')
        else:
            action_index = self.random.choice(len(pi), p=pi)

        action = valid_actions[action_index]

        return action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        a = self.predict(board, state, 'Action')
        return a if a else Wait(self.team)

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        r = self.predict(board, state, 'Response')
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
