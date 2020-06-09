import logging

import numpy as np

from core import ACTION_MOVE, ACTION_ATTACK
from core.actions import Shoot
from core.game import scenarios


class PlayerDummy:

    def __init__(self, team: str):
        self.name = 'dummy'
        self.team = team

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseFigure(self, figures: list):
        return np.random.choice(figures)

    def chooseActionType(self, types: list):
        return np.random.choice(types)

    def chooseAction(self, actions: list):
        return np.random.choice(actions)

    def chooseResponse(self):
        return np.random.choice([True, False])


class MatchManager:

    def __init__(self, scenario: str, red: PlayerDummy, blue: PlayerDummy, seed: int = 42):
        self.gm = getattr(scenarios, scenario)()
        self.red = red
        self.blue = blue
        self.seed = seed
        self.scenario = scenario

        self.actionsDone = []

        self.turn = -1
        self.end = False
        self.first: PlayerDummy = red
        self.second: PlayerDummy = blue
        self.step = None

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

        logging.info(f'Turn {self.turn}')

    def _goRound(self):
        logging.info('step: round')
        try:
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

            self.actionsDone.append(action)
            self.gm.activate(action)

        except ValueError as e:
            logging.info(e)

        finally:
            self.step = self._goResponse

    def _goResponse(self):
        action = self.actionsDone[-1]
        if isinstance(action, Shoot):
            logging.info('step: response')
            responses = self.gm.buildResponses(self.second.team, action.target)

            if responses:
                if np.random.choice([True, False]):
                    response = np.random.choice(responses)

                    self.actionsDone.append(response)
                    self.gm.activate(response)
                else:
                    logging.info('no response given')
            else:
                logging.info('no response available')

            self.first, self.second = self.second, self.first
            self.step = self._goCheck

        else:
            self.first, self.second = self.second, self.first
            self._goCheck()

    def _goCheck(self):
        if self.gm.activableFigures(self.first.team) or self.gm.activableFigures(self.second.team):
            self.step = self._goRound
        elif self.gm.goalAchieved():
            self.step = self._goEnd
        else:
            self.step = self._goUpdate

    def _goUpdate(self):
        logging.info('step: update')

        self.turn += 1
        self.gm.update()

        self.step = self._goCheck
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
        while self.turn == t:
            self.step()
