import logging

import numpy as np

import agents.players as players
import scenarios
from agents.players.player import Player
from core import TOTAL_TURNS
from core.actions import Shoot, Move
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'actionsDone', 'outcome', 'end', 'board', 'state', 'gm', 'scenario', 'red', 'blue',
        'first', 'second', 'step',
    ]

    def __init__(self, gid: str, scenario: str, red: str, blue: str, seed: int = 42):
        """
        Initialize the state-machine.

        :param gid:         Unique identifier.
        :param scenario:    String value of the scenario to use. Check module scenarios for a list.
        :param red:         String value of the player to use. Check module agent.players for a list.
        :param blue:        String value of the player to use. Check module agent.players for a list.
        :param seed:        Random seed value (default: 42)
        """
        self.gid: str = gid
        self.seed: int = seed

        self.actionsDone: list = []
        self.outcome: list = []

        self.end: bool = False

        self.gm: GameManager = GameManager()

        self.scenario: str = scenario
        board, state = getattr(scenarios, scenario)()
        self.board: GameBoard = board
        self.state: GameState = state

        self.red: Player = getattr(players, red)('red')
        self.blue: Player = getattr(players, blue)('blue')

        self._goInit()

    def reset(self):
        _, state = getattr(scenarios, self.scenario)()
        self.state: GameState = state
        self._goInit()

    def _goInit(self):
        logging.info('step: init')
        logging.info(f'SCENARIO: {self.board.name}')
        logging.info(f'SEED:     {self.seed}')

        np.random.seed(self.seed)

        self.end = False

        self.step = self._goUpdate

    def _goRound(self):
        logging.info(f'step: round {self.first.team:5}')

        try:
            action = self.first.chooseAction(self.gm, self.board, self.state)
            outcome = self.gm.step(self.board, self.state, action)

            self.actionsDone.append(action)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(f'{self.first.team:5}: {e}')

        finally:
            self._goCheck()

    def _goResponse(self):
        logging.info(f'step: response {self.second.team:5}')

        try:
            response = self.second.chooseResponse(self.gm, self.board, self.state)
            logging.info(f'{self.second} respond')

            outcome = self.gm.step(self.board, self.state, response)

            self.actionsDone.append(response)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(f'{self.second.team:5}: {e}')

        finally:
            self._goCheck()

    def _goCheck(self):
        logging.info('-' * 100)

        # check if we are at the end of the game
        if self.gm.goalAchieved(self.board, self.state) or self.state.turn >= TOTAL_TURNS:
            # if we achieved a goal, end
            self.step = self._goEnd
            return

        if self.step == self._goRound:
            # after a round we have a response
            action = self.actionsDone[-1] if len(self.actionsDone) > 0 else None

            if isinstance(action, Shoot) or isinstance(action, Move):
                self.step = self._goResponse
                return

        if self.state.getFiguresActivatable(self.first.team) or self.state.getFiguresActivatable(self.second.team):
            # if there are still figure to activate, continue with a round
            if not self.step == self._goUpdate:
                # invert only if it is not an update
                self.first, self.second = self.second, self.first

            self.step = self._goRound

        else:
            # if we are at the end of a turn, need to update and then go to next one
            self.step = self._goUpdate

    def _goUpdate(self):
        logging.info('=' * 100)
        logging.info('step: update')

        self.first = self.red
        self.second = self.blue

        self.gm.update(self.state)
        logging.info(f'Turn {self.state.turn}')

        self._goCheck()

    def _goEnd(self):
        logging.info("step: end")
        self.end = True
        self.step = self._goEnd

    def nextStep(self):
        logging.info('next: step')

        self.step()

    def nextTurn(self):
        logging.info('next: turn')

        t = self.state.turn
        while self.state.turn == t and not self.end:
            self.nextStep()
