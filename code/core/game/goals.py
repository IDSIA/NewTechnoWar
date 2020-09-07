from typing import List
import numpy as np
from core.game import BLUE, RED
from core.game.state import GameState
from utils.coordinates import to_cube, Cube, cube_distance, cube_to_hex


class Goal:
    """A team has a specific goal."""
    __slots__ = ['team']

    def __init__(self, team: str):
        self.team = team

    def check(self, state: GameState) -> bool:
        raise NotImplementedError()

    def score(self, state: GameState) -> float:
        return 0


class GoalEliminateOpponent(Goal):
    """The team wins if all the hostile figures are killed."""

    def __init__(self, team: str, hostiles: str):
        super().__init__(team)
        self.hostiles: str = hostiles

    def check(self, state: GameState) -> bool:
        alive = [f for f in state.figures[self.hostiles] if not f.killed]
        return len(alive) == 0

    def score(self, state: GameState):
        score = 0

        for f in state.figures[self.team]:
            score += -2 if f.killed else +1

        for f in state.figures[self.hostiles]:
            score += +5 if f.killed else 0

        return score


class GoalReachPoint(Goal):
    """The team wins when one unit stays on the objective for the given amount of turns."""

    __slots__ = ['turns', 'objectives', 'entered', 'values']

    def __init__(self, team: str, shape: tuple, *objectives: tuple, turns: int = 1):
        # TODO: this version support 1 turn maximum!
        super().__init__(team)

        self.objectives: List[Cube] = []

        self.values = np.zeros(shape)

        # self.turns = turns
        # self.entered: Dict[(Cube, int), int] = {}

        for o in objectives:
            if len(o) == 2:
                o = to_cube(o)
            self.objectives.append(o)

        for x, y in np.ndindex(shape):
            xy = to_cube((x, y))
            for o in self.objectives:
                self.values[x, y] = cube_distance(xy, o)

        maxBV = np.max(self.values)

        for x, y in np.ndindex(shape):
            self.values[x, y] = 1 - self.values[x, y] / maxBV

        for o in objectives:
            self.values[o] = 5

    def check(self, state: GameState) -> bool:
        # for figure in state.figures[self.team]:
        #     key = (figure.position, figure.index)
        #
        #     if figure.position in self.objectives:
        #         if key not in self.entered:
        #             self.entered[key] = state.turn
        #         elif state.turn - self.entered[key] >= self.turns:
        #             return True
        #     else:
        #         for o in self.objectives:
        #             key = (o, figure.index)
        #             if key in self.entered:
        #                 del self.entered[key]
        for obj in self.objectives:
            figures = state.getFiguresByPos(self.team, obj)
            for f in figures:
                if not f.activated:
                    return True

        return False

    def score(self, state: GameState) -> float:
        score = 0

        for figure in state.getFigures(self.team):
            if not figure.killed:
                score += 2. * self.values[cube_to_hex(figure.position)] + 1

        return score


class GoalDefendPoint(GoalReachPoint):
    """
    The "Defend a position" goal is a subject to another goal like a time limit or mandatory kill.
    It is always false up until another goal is reached.
    """

    def __init__(self, team: str, hostiles: str, *objectives: tuple, turns: int = 1):
        super().__init__(team, turns=turns, *objectives)
        self.hostiles = hostiles

    def check(self, state: GameState) -> bool:
        return False

    def score(self, state: GameState) -> float:
        score = 0

        for figure in state.getFigures(self.hostiles):
            if not figure.killed:
                score -= 0.2 * self.values[cube_to_hex(figure.position)] + 1

        return score


class GoalMaxTurn(Goal):
    """The team wins when the maximum number of turns is achieved."""

    def __init__(self, team: str, turn_max: int):
        super().__init__(team)
        self.turn_max = turn_max

    def check(self, state: GameState) -> bool:
        return state.turn + 1 >= self.turn_max

    def score(self, state: GameState) -> float:
        return 10.0 / (self.turn_max - state.turn + 1)


def goalAchieved(board, state: GameState) -> (bool, str):
    """Checks if the goals are achieved or not. If yes, returns the winner team."""
    redObj = [g.check(state) for g in board.objectives[RED]]
    blueObj = [g.check(state) for g in board.objectives[BLUE]]

    if any(redObj):
        # red wins
        return True, RED

    if any(blueObj):
        # blue wins
        return True, BLUE

    return False, None
