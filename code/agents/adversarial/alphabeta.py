import logging
import math
from time import time
from typing import Tuple, List, Dict

from agents.interface import Agent
from agents.matchmanager import MatchManager
from agents.adversarial.greedy import GreedyAgent
from agents.adversarial.puppets import Puppet
from agents.commons import stateScore
from core.actions import Action
from core.const import RED, BLUE
from core.game import GameBoard, GameState, GoalParams
from core.game.outcome import Outcome
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class AlphaBetaAgent(Agent):

    def __init__(self, team: str, maxDepth: int = 3, timeLimit: int = 20, goal_params: GoalParams = GoalParams(),
                 seed: int = 42):
        """
        :param team:        the color of the team for this agent
        :param maxDepth:    max search depth (default: 3)
        :param timeLimit:   max execution time in seconds (default: 20)
        :param goal_params: parameters used for the evaluation of the state
        :param seed:        internal random seed (default: 42)
        """
        super().__init__('AlphaBetaAgent', team, seed)

        self.maxDepth: int = maxDepth
        self.timeLimit: int = timeLimit

        # cache for the explored states
        self.cache: Dict[Tuple[int, int], Tuple[GameState, Outcome]] = {}
        self.goal_params: GoalParams = goal_params

        # these pseudo-agents are used only internally, the cannot perform any action
        self.puppets: dict = {RED: Puppet(RED), BLUE: Puppet(BLUE)}
        # internal and controlled MatchManager
        self.mm: MatchManager = MatchManager('', self.puppets[RED], self.puppets[BLUE], seed=seed, useLoggers=False)

        self.searchCutOff: bool = False
        self.forceHit: bool = False

    def dataFrameInfo(self) -> List[str]:
        """
        The additional columns are:
            - score:    score associated with the chosen action
            - action:   action performed

        :return: a list with the name of the columns used in the dataframe
        """
        return super().dataFrameInfo() + [
            'score', 'action'
        ]

    def store(self, state: GameState, bestScore: float, bestAction: Action) -> None:
        """
        Wrapper of the register() method that does some pre-processing on the data that will be saved.

        :param state:           state of the game
        :param bestScore:       score of the best action found
        :param bestAction:      best action found
        """

        data = [bestScore, type(bestAction).__name__, self.maxDepth]

        self.register(state, data)

    def activateAction(self, board: GameBoard, state: GameState, action: Action) -> Tuple[GameState, Outcome]:
        """
        Internal method to perform an action. If the action and the input states have been already explored, the cached
        value is used instead of apply the action again.

        :param board:   board of the game
        :param state:   the given action will be applied to this state
        :param action:  action to apply to the given state
        :return: a tuple with the new state and the outcome of the action applied on the previous state
        """
        hashState0: int = hash(state)
        hashAction: int = hash(action.__str__())

        key = (hashState0, hashAction)

        if key in self.cache:
            return self.cache[key]

        state1, outcome = self.gm.activate(board, state, action, self.forceHit)
        self.cache[key] = state1, outcome
        return state1, outcome

    def evaluateState(self, team: str, board: GameBoard, state: GameState) -> float:
        """
        Assign a score to the given state using the stateScore() function. This

        :param team:    team to evaluate for
        :param board:   board of the game
        :param state:   the given state to be evaluated
        :return: the score assigned to this state
        """
        return stateScore(team, self.goal_params, board, state)

    def nextActions(self, team: str, board: GameBoard, state: GameState, step: str, depth: int) -> List[Action]:
        """
        Generates a list of possible actions or responses.

        By overriding this method you need to use the parameter "step" to discriminate between actions and responses. It
        is mandatory to return a list of "Response" when the step value equals to "response".

        :param team:    find the next actions for this team
        :param board:   board of the game
        :param state:   current state of the game
        :param step:    if "response", this method will generate the possible next actions
        :param depth:   current depth of the exploration
        :return: a list of the available actions that can be applied
        """
        nextActions = []
        if step == 'response':
            nextActions = self.gm.buildResponsesForTeam(board, state, team)

        else:
            nextActions = self.gm.buildActionsForTeam(board, state, team)

        return nextActions

    def apply(self, board: GameBoard, state: GameState, action: Action, step: str, alpha: float, beta: float,
              depth: int, startTime: float, timeLimit: float) -> float:
        """
        Performs an exploration of the moves tree after the application of the given action. First the given action will
        be activated with the "activateAction()" method, then the score will be assigned by exploring the tree with the
        "alphaBeta()".

        If you override this method, remember to invoke the "alphaBeta()" method to continue the exploration.

        :param board:       board of the game
        :param state:       current state
        :param action:      action to apply to the current state
        :param step:        kind of step to perform
        :param alpha:       maximization value
        :param beta:        minimization value
        :param depth:       current depth
        :param startTime:   when the search started
        :param timeLimit:   when the search ended
        :return: the score associated with this exploration
        """
        s1, _ = self.activateAction(board, state, action)
        score, _ = self.alphaBeta(board, s1, depth - 1, alpha, beta, startTime, timeLimit)
        return score

    def alphaBeta(self, board: GameBoard, state: GameState, depth: int, alpha: float, beta: float, startTime: float,
                  timeLimit: float) -> Tuple[float, Action or None]:
        """
        Perform the exploration of a branch in the tree of moves.

        :param board:       board of the game
        :param state:       current state
        :param alpha:       maximization value
        :param beta:        minimization value
        :param depth:       current depth
        :param startTime:   when the search started
        :param timeLimit:   when the search ended
        :return: a tuple composed by the score and the best Action found
        """
        currentTime = time()
        elapsedTime = currentTime - startTime

        if elapsedTime >= timeLimit:
            self.searchCutOff = True

        self.mm.loadState(board, state)
        step, team, _ = self.mm.nextPlayer()

        # if an update is required
        if step == 'update':
            self.mm.step()
            step, team, _ = self.mm.nextPlayer()

        # if this is a terminal node, abort the search
        if self.searchCutOff or depth == 0 or step == 'end' or team == '':
            score = self.evaluateState(self.team, board, state)
            return score, None

        # build actions
        nextActions = self.nextActions(team, board, state, step, depth)

        # this team maximize...
        if team == self.team:
            value = -math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                score = self.apply(board, state, nextAction, step, alpha, beta, depth, startTime, timeLimit)

                if score > value:
                    value, action = score, nextAction
                    logging.debug(f'      AB{depth}: Max {action} [{score}]')

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value, action

        # ...other minimize
        else:
            value = math.inf
            action = None
            for nextAction in nextActions:
                logging.debug(f'{depth:<4}{team:5}{step:6}{nextAction}')

                score = self.apply(board, state, nextAction, step, alpha, beta, depth, startTime, timeLimit)

                if score < value:
                    value, action = score, nextAction
                    logging.debug(f'       AB{depth}: Min {action} [{score}]')

                beta = min(beta, value)

                if beta <= alpha:
                    break

            return value, action

    def search(self, board: GameBoard, state: GameState) -> Tuple[float, Action]:
        """
        Search for the best action using iterative deepening search and Alpha-Beta pruning.

        :param board:   board of the game
        :param state:   starting state
        :return: a tuple composed by the score and the best Action found
        """

        startTime: float = time()
        endTime: float = startTime + self.timeLimit
        score: float = 0
        action: Action or None = None
        self.searchCutOff = False

        for depth in range(1, self.maxDepth):
            currentTime: float = time()

            if currentTime >= endTime:
                break

            score, action = self.alphaBeta(board, state, depth, -math.inf, math.inf, currentTime, endTime - currentTime)

        if not action:
            raise ValueError('no action given')

        return score, action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        """
        Uses the search() method to find the next best action to perform.

        :param board:   board of the game
        :param state:   the current state
        :return: the next action to apply
        """
        score, action = self.search(board, state)

        self.store(state, score, action)

        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        """
        Uses the search() method to find the next best response to perform.

        :param board:   board of the game
        :param state:   the current state
        :return: the next response to apply
        """
        score, action = self.search(board, state)

        self.store(state, score, action)

        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """
        Uses GreedyAgent's placer() method.

        :param board:   board of the game
        :param state:   the current state
        """

        # TODO: find a better placer
        ga = GreedyAgent(self.team)
        ga.placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        """
        Plays a quick game with each color and choose the color with the best score.

        :param board:   board of the game
        :param state:   the current state
        """
        colors = list(state.choices[self.team].keys())

        max_color = None
        max_value = -math.inf

        for color in colors:
            s: GameState = deepcopy(state)
            s.choose(self.team, color)
            score, _ = self.search(board, s)

            if score > max_value:
                max_value = score
                max_color = color

        state.choose(self.team, max_color)
        logging.info(f'{self.team:5}: choose positions color {max_color}')
