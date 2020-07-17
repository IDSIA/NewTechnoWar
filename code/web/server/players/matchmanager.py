import logging

import numpy as np

import web.server.players as players
from core import ACTION_MOVE, ACTION_ATTACK
from core.actions import Shoot, Pass
from core.game import scenarios
from core.game.manager import GameManager
from web.server.players.player import Player


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'actionsDone', 'outcome', 'turn', 'end', 'update', 'gm', 'scenario', 'red', 'blue', 'first',
        'second', 'step'
    ]

    def __init__(self, gid: str, scenario: str, red: str, blue: str, seed: int = 42):
        self.gid: str = gid
        self.seed: int = seed

        self.actionsDone: list = []
        self.outcome: list = []

        self.turn: int = -1
        self.end: bool = False
        self.update: bool = False

        self.scenario: str = scenario
        self.gm: GameManager = getattr(scenarios, scenario)()

        self.red: Player = getattr(players, red)('red')
        self.blue: Player = getattr(players, blue)('blue')

        self._goInit()

    def _goInit(self):
        logging.info('step: init')
        logging.info(f'SCENARIO: {self.gm.name}')
        logging.info(f'SEED: {self.seed}')

        np.random.seed(self.seed)

        self.turn = 0
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
            figures = self.gm.activableFigures(self.first.team)
            if not figures:
                raise ValueError(f"no more figures for {self.first}")

            f = self.first.chooseFigure(figures)

            moves = self.gm.buildMovements(self.first.team, f)
            shoots = self.gm.buildShoots(self.first.team, f)

            if not moves and not shoots:
                raise ValueError(f"no more moves for {f} {self.first}")

            whatDo = []

            if moves:
                whatDo.append(ACTION_MOVE)
            if shoots:
                whatDo.append(ACTION_ATTACK)

            # agent chooses type of action
            toa = self.first.chooseActionType(whatDo)

            actions = []

            if toa == ACTION_MOVE:
                actions = moves

            if toa == ACTION_ATTACK:
                actions = shoots

            action = self.first.chooseAction(actions)
            outcome = self.gm.activate(action)

            self.actionsDone.append(action)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(e)

        finally:
            self._goCheck()

    def _goResponse(self):
        logging.info('step: response')

        self.update = False
        action = self.actionsDone[-1]
        responses = self.gm.buildResponses(self.second.team, action.target)

        if responses:
            if np.random.choice([True, False]):
                response = np.random.choice(responses)
                outcome = self.gm.activate(response)

                self.actionsDone.append(response)
                self.outcome.append(outcome)
            else:
                logging.info('no response given')
                self.actionsDone.append(Pass(self.second.team, action.target))
        else:
            logging.info('no response available')
            self.actionsDone.append(Pass(self.second.team, action.target))

        self._goCheck()

    def _goCheck(self):
        action = self.actionsDone[-1]
        if isinstance(action, Shoot):
            self.step = self._goResponse
        else:
            if self.gm.activableFigures(self.first.team) or self.gm.activableFigures(self.second.team):
                self.first, self.second = self.second, self.first
                self.step = self._goRound
            elif self.gm.goalAchieved():
                self.step = self._goEnd
            else:
                self.step = self._goUpdate

    def _goUpdate(self):
        logging.info('step: update')

        self.turn += 1
        self.gm.update()

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
