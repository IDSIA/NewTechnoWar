import logging
from typing import List, Tuple, Dict

from utils.copy import deepcopy

import numpy as np

import agents as players
import scenarios
from agents import Agent
from agents.interactive.interactive import Human
from core import GM
from core.actions import Attack, Move, Action, Response
from core.const import RED, BLUE
from core.game.board import GameBoard
from core.game.goals import goalAchieved
from core.game.state import GameState


def buildMatchManager(gid: str, scenario: str, red: str, blue: str, seed: int = 42):
    """Utility function to create a standard MatchManager from string parameters."""
    board, state = getattr(scenarios, scenario)()

    pRed: Agent = getattr(players, red)(RED)
    pBlue: Agent = getattr(players, blue)(BLUE)

    return MatchManager(gid, pRed, pBlue, board, state, seed)


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'states_history', 'actions_history', 'outcome', 'end', 'board', 'state', 'origin', 'gm',
        'scenario', 'red', 'blue',
        'first', 'second', 'step', 'update', 'winner', 'humans'
    ]

    def __init__(self, gid: str, red: Agent, blue: Agent, board: GameBoard = None, state: GameState = None,
                 seed: int = 42):
        """
        Initialize the state-machine.

        :param gid:         Unique identifier.
        :param board:       Static descriptor of the game.
        :param state:       Dynamic descriptor of the game.
        :param red:         String value of the player to use. Check module agent.interactive for a list.
        :param blue:        String value of the player to use. Check module agent.interactive for a list.
        :param seed:        Random seed value (default: 42)
        """
        self.gid: str = gid
        self.seed: int = seed

        self.actions_history: List[Action] = []
        self.states_history: List[GameState] = []

        self.outcome: List[dict] = []

        self.winner: str = ''
        self.end: bool = False
        self.update: bool = False

        self.board: GameBoard = board
        self.state: GameState = state
        self.origin: GameState = deepcopy(state)

        self.red: Agent = red
        self.blue: Agent = blue
        self.humans: bool = isinstance(self.red, Human) or isinstance(self.blue, Human)

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

    def _store(self, state: GameState, action: Action = None, outcome: dict = None):
        self.states_history.append(state)
        self.actions_history.append(action)
        self.outcome.append(outcome if outcome else {})

    def _goInit(self):
        """Initialization step."""
        logging.debug('step: init')
        logging.info(f'SCENARIO: {self.board.name}')
        logging.info(f'SEED:     {self.seed}')

        np.random.seed(self.seed)

        self.end = False

        # check for need of choice
        if self.state.has_choice[RED]:
            self.red.chooseFigureGroups(self.board, self.state)
        if self.state.has_choice[BLUE]:
            self.blue.chooseFigureGroups(self.board, self.state)

        # check for need of placement
        if self.state.has_placement[RED]:
            self.red.placeFigures(self.board, self.state)
        if self.state.has_placement[BLUE]:
            self.blue.placeFigures(self.board, self.state)

        self.state.completeInit()

        self.step = self._goUpdate
        self._goUpdate()

    def _goRound(self):
        """Round step."""
        logging.debug(f'step: round {self.first.team:5}')
        self.update = False
        copystate = deepcopy(self.state)  # salvare lo state self.state(una copia deep copy)

        try:
            action = self.first.chooseAction(self.board, self.state)
            outcome = GM.step(self.board, self.state, action)

            self._store(copystate, action, outcome)

        except ValueError as e:
            logging.info(f'{self.first.team:5}: {e}')
            self._store(copystate)

        finally:
            self._goCheck()

    def _goResponse(self):
        """Response step."""
        logging.debug(f'step: response {self.second.team:5}')
        copystate = deepcopy(self.state)

        try:
            response = self.second.chooseResponse(self.board, self.state)
            outcome = GM.step(self.board, self.state, response)

            logging.debug(f'{self.second.team} respond')

            self._store(copystate, response, outcome)

        except ValueError as e:
            logging.info(f'{self.second.team:5}: {e}')
            self._store(copystate)

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

        firsts = self.state.getFiguresCanBeActivated(self.first.team)
        seconds = self.state.getFiguresCanBeActivated(self.second.team)
        if firsts or seconds:
            # if there are still figure to activate, continue with a round
            if self.step == self._goUpdate:
                self.first, self.second = self.red, self.blue
            else:
                # invert only if it is not an update and seconds still have figures
                if seconds:
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

    def getPlayer(self, team) -> Agent:
        """Get the player agent by team color."""
        if team == RED:
            return self.red
        return self.blue

    def nextPlayer(self) -> Tuple:
        """Returns the next step, the next player, and if it is human or not"""
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

        return step, nextPlayer, nextHuman

    def nextPlayerDict(self) -> Dict:
        step, nextPlayer, nextHuman = self.nextPlayer()
        return {
            'step': step,
            'player': nextPlayer,
            'isHuman': nextHuman
        }

    def loadState(self, board: GameBoard, state: GameState) -> None:
        """Use this method to override the current state of a MatchManager object."""
        self.board = board
        self.state = state

        self.end = False
        self.update = False

        action: Action = state.lastAction
        self.actions_history.append(action)

        if not action:
            self.step = self._goUpdate
            self.update = True
            self.first = self.red
            self.second = self.blue

        elif isinstance(action, Response):
            self.step = self._goResponse

            if action.team == RED:
                self.first = self.blue
                self.second = self.red
            else:
                self.first = self.red
                self.second = self.blue

        else:
            self.step = self._goRound

            if action.team == RED:
                self.first = self.red
                self.second = self.blue
            else:
                self.first = self.blue
                self.second = self.red

        self._goCheck()
