import logging
from typing import List
from typing import Tuple, Dict

import agents as players
from agents.interface import Agent
from agents.interactive.interactive import Human
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam
from core.const import RED, BLUE
from core.game import GameBoard, GameState, goalAchieved, goalScore, GameManager, GoalParams, Outcome
from core.scenarios import buildScenario
from utils.copy import deepcopy


def buildMatchManager(gid: str, scenario: str, red: str, blue: str, seed: int = 42):
    """
    Utility function to create a standard MatchManager from string parameters.

    :param gid: game unique id
    :param scenario: scenario to use
    :param red: red agent to use
    :param blue: blue agent to use
    :param seed: seed to use
    :return: a configured MatchManager
    """
    board, state = buildScenario(scenario)

    pRed: Agent = getattr(players, red)(RED)
    pBlue: Agent = getattr(players, blue)(BLUE)

    return MatchManager(gid, pRed, pBlue, board, state, seed)


class MatchManager:
    __slots__ = [
        'gid', 'seed', 'states_history', 'actions_history', 'outcome', 'end', 'board', 'state', 'origin', 'gm',
        'scenario', 'red', 'blue', 'first', 'second', 'step', 'update', 'winner', 'humans', 'logger', 'score', 'p'
    ]

    def __init__(self, gid: str, red: Agent, blue: Agent, board: GameBoard = None, state: GameState = None,
                 seed: int = 42, useLoggers: bool = True, p_red: GoalParams = GoalParams(), p_blue: GoalParams = GoalParams()):
        """
        Initialize the state-machine.

        :param gid:         Unique identifier.
        :param board:       Static descriptor of the game.
        :param state:       Dynamic descriptor of the game.
        :param red:         String value of the player to use. Check module agent.interactive for a list.
        :param blue:        String value of the player to use. Check module agent.interactive for a list.
        :param seed:        Random seed value (default: 42)
        """
        if useLoggers:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger("internal")

        self.gid: str = gid
        self.seed: int = seed

        self.actions_history: List[Action] = []
        self.states_history: List[GameState] = []

        self.outcome: List[Outcome] = []

        self.winner: str = ''
        self.end: bool = False
        self.update: bool = False

        self.board: GameBoard = board
        self.state: GameState = state
        self.origin: GameState = deepcopy(state)

        self.gm: GameManager = GameManager(self.seed)

        self.red: Agent = red
        self.blue: Agent = blue
        self.humans: bool = isinstance(self.red, Human) or isinstance(self.blue, Human)

        self.first = None
        self.second = None

        self.score: dict[str, float] = {
            RED: 0,
            BLUE: 0,
        }

        self.p: dict[str, GoalParams] = {
            RED: p_red,
            BLUE: p_blue,
        }

        if board and state:
            self.loadState(board, state)

    def reset(self) -> None:
        """Restore the match to its original (before initialization) stage."""
        self.state: GameState = deepcopy(self.origin)
        self.gm: GameManager = GameManager(self.seed)

        self.actions_history = []
        self.outcome = []

        self.winner = ''
        self.end = False
        self.update = False

        self._goInit()

    def _store(self, state: GameState, action: Action = None, outcome: Outcome = None) -> None:
        """
        Saves in the internal history the state of the game, the action, and its outcome.

        :param state:       state of the game before applying the action
        :param action:      the action applied
        :param outcome:     outcome after the action was applied to the state
        """
        self.states_history.append(state)
        self.actions_history.append(action)
        self.outcome.append(outcome if outcome else Outcome())

    def _goInit(self) -> None:
        """Initialization step."""
        self.logger.debug('step: init')
        self.logger.info(f'{self.seed:10} SCENARIO: {self.board.name}')
        self.logger.info(f'{self.seed:10} SEED:     {self.seed}')

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

    def _goRound(self) -> None:
        """Round step."""
        self.logger.debug(f'{self.seed:10} step: round {self.first.team:5}')
        self.update = False
        state0 = deepcopy(self.state)

        try:
            action = self.first.chooseAction(self.board, self.state)
        except ValueError as e:
            self.logger.debug(f'{self.seed:10} {self.first.team:5} {"exception":9}: {e}')
            action = PassTeam(self.first.team)

        outcome = self.gm.step(self.board, self.state, action)

        self._store(state0, action, outcome)
        self.logger.info(f'{self.seed:10} {self.first.team:5} {self.score[self.first.team]:6.2f} {"action":9}: {action} {outcome.comment}')

        self._goCheck()

    def _goResponse(self) -> None:
        """Response step."""
        self.logger.debug(f'{self.seed:10} step: response {self.second.team:5}')
        state0 = deepcopy(self.state)

        try:
            response = self.second.chooseResponse(self.board, self.state)
        except ValueError as e:
            self.logger.debug(f'{self.seed:10} {self.second.team:5} {"exception":9}: {e}')
            response = NoResponse(self.second.team)

        outcome = self.gm.step(self.board, self.state, response)

        self._store(state0, response, outcome)
        self.logger.info(f'{self.seed:10} {self.second.team:5} {self.score[self.second.team]:6.2f} {"response":9}: {response} {outcome.comment}')

        self._goCheck()

    def _goCheck(self) -> None:
        """Check next step to do."""

        # check if state has been initialized
        if not self.state.initialized:
            self.step = self._goInit
            self.logger.info(f'State is not initialized')
            return

        # check if we are at the end of the game
        isEnd, winner = goalAchieved(self.board, self.state)

        self.score[RED] = goalScore(self.board, self.state, RED, self.p[RED])
        self.score[BLUE] = goalScore(self.board, self.state, BLUE, self.p[BLUE])

        if isEnd:
            # if we achieved a goal, end
            self.winner = winner
            self.step = self._goEnd
            self.logger.info(f'{self.seed:10} End game! Winner is {winner}')
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

    def _goUpdate(self) -> None:
        """Update step."""
        self.logger.info(f'{self.seed:10} ' + ('=' * 50))
        self.logger.debug(f'{self.seed:10} step: update')
        self.update = True

        self.first = self.red
        self.second = self.blue

        self.gm.update(self.state)
        self.logger.info(f'{self.seed:10} Turn {self.state.turn}')

        self._goCheck()

    def _goEnd(self) -> None:
        """End step."""
        self.logger.debug(f'{self.seed:10} step: end')
        self.end = True
        self.update = False
        self.step = self._goEnd

    def nextStep(self) -> None:
        """Go to the next step"""
        self.logger.debug('{self.seed:10} next: step')
        self.step()

    def nextTurn(self) -> None:
        """Continue to execute nextStep() until the turn changes."""
        self.logger.debug(f'{self.seed:10} next: turn')

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
        """
        Used for web interface.
        :return: a dictionary with the next step, player, and if it is human
        """
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

    def play(self) -> None:
        """Plays a match until the end is reached."""
        while not self.end:
            self.nextStep()
