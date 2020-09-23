import logging
from utils.copy import deepcopy

import numpy as np

import agents as players
import scenarios
from agents.players.player import Player
from core import GM
from core.actions import Attack, Move
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import goalAchieved
from core.game.state import GameState


def buildMatchManager(gid: str, scenario: str, red: str, blue: str, seed: int = 42):
    """Utility function to create a standard MatchManager from string parameters."""
    board, state = getattr(scenarios, scenario)()

    pRed: Player = getattr(players, red)(RED)
    pBlue: Player = getattr(players, blue)(BLUE)

    return MatchManager(gid, board, state, pRed, pBlue, seed)


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'actions_history', 'outcome', 'end', 'board', 'state', 'origin', 'gm', 'scenario', 'red', 'blue',
        'first', 'second', 'step', 'update', 'winner',
    ]

    def __init__(self, gid: str, board: GameBoard, state: GameState, red: Player, blue: Player, seed: int = 42):
        """
        Initialize the state-machine.

        :param gid:         Unique identifier.
        :param board:       Static descriptor of the game.
        :param state:       Dynamic descriptor of the game.
        :param red:         String value of the player to use. Check module agent.players for a list.
        :param blue:        String value of the player to use. Check module agent.players for a list.
        :param seed:        Random seed value (default: 42)
        """
        self.gid: str = gid
        self.seed: int = seed

        self.actions_history: list = []
        self.outcome: list = []

        self.winner: str = ''
        self.end: bool = False
        self.update: bool = False

        self.board: GameBoard = board
        self.state: GameState = state
        self.origin: GameState = deepcopy(state)

        self.red: Player = red
        self.blue: Player = blue

        self.first = None
        self.second = None

        self.step = self._goInit

    def reset(self):
        """Restore the match to its original (before initialization) stage."""
        self.state: GameState = deepcopy(self.origin)

        self.actions_history = []
        self.outcome = []

        self.winner = ''
        self.end = False
        self.update = False

        self._goInit()

    def _goInit(self):
        """Initialization step."""
        logging.debug('step: init')
        logging.info(f'SCENARIO: {self.board.name}')
        logging.info(f'SEED:     {self.seed}')

        np.random.seed(self.seed)

        self.end = False

        # check for need of placement
        if self.state.has_placement[RED]:
            self.red.placeFigures(self.board, self.state)
        if self.state.has_placement[BLUE]:
            self.blue.placeFigures(self.board, self.state)

        # check for need of choice
        if self.state.has_choice[RED]:
            self.red.chooseFigureGroups(self.board, self.state)
        if self.state.has_choice[BLUE]:
            self.blue.chooseFigureGroups(self.board, self.state)

        self.state.completeInit()

        self.step = self._goUpdate
        self._goUpdate()

    def _goRound(self):
        """Round step."""
        logging.debug(f'step: round {self.first.team:5}')
        self.update = False

        try:
            action = self.first.chooseAction(self.board, self.state)
            outcome = GM.step(self.board, self.state, action)

            self.actions_history.append(action)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(f'{self.first.team:5}: {e}')
            self.actions_history.append(None)

        finally:
            self._goCheck()

    def _goResponse(self):
        """Response step."""
        logging.debug(f'step: response {self.second.team:5}')

        try:
            response = self.second.chooseResponse(self.board, self.state)
            outcome = GM.step(self.board, self.state, response)

            logging.info(f'{self.second.team} respond')

            self.actions_history.append(response)
            self.outcome.append(outcome)

        except ValueError as e:
            logging.info(f'{self.second.team:5}: {e}')
            self.actions_history.append(None)
            self.outcome.append({})

        finally:
            self._goCheck()

    def _goCheck(self):
        """Check next step to do."""
        # check if we are at the end of the game
        isEnd, winner = goalAchieved(self.board, self.state)
        if isEnd:
            # if we achieved a goal, end
            self.winner = winner
            self.step = self._goEnd
            logging.info(f'End game! Winner is {winner}')
            return

        if self.step == self._goRound:
            # after a round we have a response
            action = self.actions_history[-1] if len(self.actions_history) > 0 else None

            if isinstance(action, Attack) or isinstance(action, Move):
                self.step = self._goResponse
                return

        if self.state.getFiguresCanBeActivated(self.first.team) or self.state.getFiguresCanBeActivated(
                self.second.team):
            # if there are still figure to activate, continue with a round
            if not self.step == self._goUpdate:
                # invert only if it is not an update
                self.first, self.second = self.second, self.first

            self.step = self._goRound
            return

        # if we are at the end of a turn, need to update and then go to next one
        self.step = self._goUpdate

    def _goUpdate(self):
        """Update step."""
        logging.info('=' * 100)
        logging.debug('step: update')
        self.update = True

        self.first = self.red
        self.second = self.blue

        GM.update(self.state)
        logging.info(f'Turn {self.state.turn}')

        self._goCheck()

    def _goEnd(self):
        """End step."""
        logging.debug("step: end")
        self.end = True
        self.update = False
        self.step = self._goEnd

    def nextStep(self):
        """Go to the next step"""
        logging.debug('next: step')
        self.step()

    def nextTurn(self):
        """Continue to execute nextStep() until the turn changes."""
        logging.debug('next: turn')

        t = self.state.turn
        while self.state.turn == t and not self.end:
            self.nextStep()

    def getPlayer(self, team):
        """Get the player agent by team color."""
        if team == RED:
            return self.red
        return self.blue

    def nextPlayer(self):
        step = ''
        nextPlayer = ''
        nextHuman = False

        if self.step == self._goInit:
            step = 'init'
        if self.step == self._goRound:
            step = 'round'
            nextPlayer = self.first.team
            nextHuman = self.first.name == 'Human'
        if self.step == self._goResponse:
            step = 'response'
            nextPlayer = self.second.team
            nextHuman = self.second.name == 'Human'
        if self.step == self._goUpdate:
            step = 'update'
        if self.step == self._goEnd:
            step = 'end'

        return {
            'step': step,
            'player': nextPlayer,
            'isHuman': nextHuman
        }
