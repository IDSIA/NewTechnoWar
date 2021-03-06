import numpy as np

from agents import Agent
from core.const import BLUE
from core.actions import Action, PassTeam, PassFigure, Wait
from core.game import GameBoard, GameState, GoalParams
from core.utils.coordinates import Hex

ACTION_MOVE = 0
ACTION_ATTACK = 1
ACTION_PASS = 2


class RandomAgent(Agent):

    def __init__(self, team: str, seed=0):
        super().__init__('RandomAgent', team, seed=seed)

        self.goal_params: GoalParams = GoalParams()
        self.maximize: bool = True

    def dataFrameInfo(self):
        return super().dataFrameInfo() + [
            'action'
        ]

    def store(self, state: GameState, bestAction: Action):
        data = [type(bestAction).__name__]

        self.register(state, data)

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        """
        Randomly choose an action between the possible ones.

        :param board:   board of the game
        :param state:   the current state
        :return: the next action to apply
        """
        # choose which figures that can still be activate will be activated
        figures = state.getFiguresCanBeActivated(self.team)
        if not figures:
            raise ValueError(f"no more figures for {self.team}")

        f = self.random.choice(figures)

        moves = self.gm.buildMovements(board, state, f)
        attacks = self.gm.buildAttacks(board, state, f)

        if not moves and not attacks:
            raise ValueError(f"no more moves for {f} {self.team}")

        whatDo = [ACTION_PASS]

        if moves:
            whatDo.append(ACTION_MOVE)
        if attacks:
            whatDo.append(ACTION_ATTACK)

        p = [[1], [0.1, 0.9], [0.1, 0.45, 0.45]]

        # agent chooses type of action
        toa = self.random.choice(whatDo, p=p[len(whatDo) - 1])

        actions = []

        if toa == ACTION_PASS:
            actions = [PassTeam(self.team), PassFigure(f)]
            if self.team == BLUE:
                actions.append(Wait(self.team))

        if toa == ACTION_MOVE:
            actions = moves

        if toa == ACTION_ATTACK:
            actions = attacks
        action = self.random.choice(actions)
        self.store(state, action)

        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        """
        Randomly choose a response between the possible ones.

        :param board:   board of the game
        :param state:   the current state
        :return: the next response to apply
        """
        # choose to respond or not
        if not self.random.choice([True, False]):
            raise ValueError('no response given')

        # choose which figures that can still respond will respond
        figures = state.getFiguresCanRespond(self.team)
        if not figures:
            raise ValueError('no figure can respond')

        f = self.random.choice(figures)

        # build possible response for the chosen unit
        responses = self.gm.buildResponses(board, state, f)

        if responses:
            response = self.random.choice(responses)
            self.store(state, response)
            return response
        else:
            raise ValueError('no response available')

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        """
        Random choose the initial position of the figures.

        :param board:   board of the game
        :param state:   the current state
        """
        # select area
        x, y = np.where(state.placement_zone[self.team] > 0)
        figures = state.getFigures(self.team)

        # choose random positions
        indices = self.random.choice(len(x), size=len(figures), replace=False)

        for i in range(len(figures)):
            # move each unit to its position
            figure = figures[i]
            dst = Hex(x[indices[i]], y[indices[i]]).cube()
            state.moveFigure(figure, figure.position, dst)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        """
        Randomly choose the group of units to use.

        :param board:   board of the game
        :param state:   the current state
        """
        # randomly choose a color
        colors = list(state.choices[self.team].keys())
        color = self.random.choice(colors)

        state.choose(self.team, color)
