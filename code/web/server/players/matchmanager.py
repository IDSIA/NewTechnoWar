import logging

import numpy as np

import scenarios
import web.server.players as players
from core.actions import Shoot, Pass
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState
from web.server.players.player import Player


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'actionsDone', 'outcome', 'turn', 'end', 'update', 'board', 'state', 'gm', 'scenario', 'red',
        'blue', 'first', 'second', 'step'
    ]

    def __init__(self, gid: str, scenario: str, red: str, blue: str, seed: int = 42):
        self.gid: str = gid
        self.seed: int = seed

        self.actionsDone: list = []
        self.outcome: list = []

        self.turn: int = -1
        self.end: bool = False
        self.update: bool = False

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
        logging.info(f'SEED: {self.seed}')

        np.random.seed(self.seed)

        self.gm.update(self.state)

        self.turn = self.state.turn
        self.first = self.red
        self.second = self.blue
        self.step = self._goRound

        self.end = False
        self.update = False

        logging.info(f'Turn {self.turn}')

    def _goRound(self):
        logging.info('step: round')
        try:
            self.update = False

            action = self.first.chooseAction(self.gm, self.board, self.state)
            outcome = self.gm.step(self.board, self.state, action)

            self.actionsDone.append(action)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(e)

        finally:
            self._goCheck()

    def _goResponse(self):
        logging.info('step: response')
        self.update = False

        try:
            response = self.second.chooseResponse(self.gm, self.board, self.state)
        except ValueError as e:
            logging.info(e)
            action = self.state.lastAction
            response = Pass(self.second.team, action.target)

        outcome = self.gm.step(self.board, self.state, response)
        self.actionsDone.append(response)
        self.outcome.append(outcome)

        self._goCheck()

    def _goCheck(self):
        action = self.actionsDone[-1]
        if isinstance(action, Shoot):
            self.step = self._goResponse
        else:
            if self.state.getFiguresActivatable(self.first.team) or self.state.getFiguresActivatable(self.second.team):
                # if there are still figure to activate, continue with the current round
                self.first, self.second = self.second, self.first
                self.step = self._goRound
            elif self.gm.goalAchieved(self.board, self.state):
                # if we achieved a goal, end
                self.step = self._goEnd
            else:
                # if we are at the end of a turn, need to update and then go to next one
                self.step = self._goUpdate

    def _goUpdate(self):
        logging.info('step: update')

        self.turn += 1
        self.gm.update(self.state)

        self._goCheck()
        self.update = True
        logging.info(f'Turn {self.turn}')

    def _goEnd(self):
        logging.info("step: end")
        self.end = True
        self.step = self._goEnd

    def nextStep(self):
        logging.info('next: step')

        self.step()

    def nextTurn(self):
        logging.info('next: turn')

        t = self.turn
        while self.turn == t and not self.end:
            self.step()
