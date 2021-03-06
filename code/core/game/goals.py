from typing import List, Tuple

import numpy as np

from core.const import BLUE, RED
from core.game.state import GameState
from core.utils.coordinates import Cube, Hex


class GoalParams:
    __slots__ = [
        'unit_team_lost', 'unit_team_alive', 'unit_enemy_killed', 'unit_enemy_alive', 'reach_team_near',
        'defend_team_near', 'defend_enemy_near', 'wait_for_turn'
    ]

    def __init__(self) -> None:
        super().__init__()

        # parameters GoalEliminateOpponent
        self.unit_team_lost: float = -2.0
        self.unit_team_alive: float = 1.0
        self.unit_enemy_killed: float = 5.0
        self.unit_enemy_alive: float = 0.0

        # parameters GoalReachPoint
        self.reach_team_near: float = 2.0

        # parameters GoalDefendPoint
        self.defend_team_near: float = 2.0
        self.defend_enemy_near: float = 0.5

        # parameters GoalMaxTurn
        self.wait_for_turn: float = 10.0

    def __repr__(self) -> str:
        return f'GoalParams'


class Goal:
    """A team has a specific goal."""
    __slots__ = ['team']

    def __init__(self, team: str):
        self.team = team

    def check(self, state: GameState) -> bool:
        raise NotImplementedError()

    def score(self, state: GameState, p: GoalParams) -> float:
        return 0


class GoalEliminateOpponent(Goal):
    """The team wins if all the hostile figures are killed."""

    def __init__(self, team: str, hostiles: str):
        super().__init__(team)
        self.hostiles: str = hostiles

    def check(self, state: GameState) -> bool:
        alive = [f for f in state.figures[self.hostiles] if not f.killed]
        return len(alive) == 0

    def score(self, state: GameState, p: GoalParams) -> float:
        score = 0

        # malus: lost a unit
        for f in state.figures[self.team]:
            score += p.unit_team_lost if f.killed else p.unit_team_alive

        # bonus kill a unit
        for f in state.figures[self.hostiles]:
            score += p.unit_enemy_killed if f.killed else p.unit_enemy_alive

        return score


class GoalReachPoint(Goal):
    """The team wins when one unit stays on the objective for the given amount of turns."""

    __slots__ = ['turns', 'objectives', 'entered', 'values']

    def __init__(self, team: str, shape: tuple, objectives: List[tuple or Hex or Cube], turns: int = 1):
        """
        This version support 1 turn maximum!
        """
        # TODO: support multiple turns
        super().__init__(team)

        self.objectives: List[Cube] = []

        self.values: np.ndarray = np.zeros(shape)

        self.turns = turns
        # self.entered: Dict[(Cube, int), int] = {}

        for o in objectives:
            if isinstance(o, Hex):
                o = o.cube()
            elif isinstance(o, tuple):
                o = Hex(t=o).cube()
            self.objectives.append(o)

        for x, y in np.ndindex(shape):
            xy = Hex(x, y).cube()
            for o in self.objectives:
                self.values[x, y] = xy.distance(o)

        maxBV = np.max(self.values)

        for x, y in np.ndindex(shape):
            self.values[x, y] = 1 - self.values[x, y] / maxBV

        for o in self.objectives:
            self.values[o.tuple()] = 5

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

    def score(self, state: GameState, p: GoalParams) -> float:
        score = 0

        # bonus: be near the target
        for figure in state.getFigures(self.team):
            if not figure.killed:
                score += p.reach_team_near * self.values[figure.position.tuple()] + 1

        return score


class GoalDefendPoint(GoalReachPoint):
    """
    The "Defend a position" goal is a subject to another goal like a time limit or mandatory kill.
    It is always false up until another goal is reached.

    This version support 1 turn maximum!
    """
    # TODO: support multiple turns

    def __init__(self, team: str, hostiles: str, shape: tuple, objectives: List[tuple], turns: int = 1):
        super().__init__(team, shape, objectives, turns=turns)
        self.hostiles = hostiles

    def check(self, state: GameState) -> bool:
        return False

    def score(self, state: GameState, p: GoalParams) -> float:
        score = 0

        # bonus: be near the target
        for figure in state.getFigures(self.team):
            if not figure.killed:
                score += p.defend_team_near * self.values[figure.position.tuple()] + 1

        # malus: having enemy units near the target
        for figure in state.getFigures(self.hostiles):
            if not figure.killed:
                score -= p.defend_enemy_near * self.values[figure.position.tuple()] + 1

        return score


class GoalMaxTurn(Goal):
    """The team wins when the maximum number of turns is achieved."""

    def __init__(self, team: str, turn_max: int):
        super().__init__(team)
        self.turn_max = turn_max

    def check(self, state: GameState) -> bool:
        return state.turn + 1 >= self.turn_max

    def score(self, state: GameState, p: GoalParams) -> float:
        # bonus: if waits until the end
        return p.wait_for_turn / (self.turn_max - state.turn + 1)


def goalAchieved(board, state: GameState) -> Tuple[bool, str]:
    """Checks if the goals are achieved or not. If yes, returns the winner team."""
    redObj = [g.check(state) for g in board.objectives[RED].values()]
    blueObj = [g.check(state) for g in board.objectives[BLUE].values()]

    if any(redObj):
        # red wins
        return True, RED

    if any(blueObj):
        # blue wins
        return True, BLUE

    return False, None


def goalScore(board, state: GameState, team: str, p: GoalParams) -> float:
    """Calculates the sum of all the scores for a team."""
    return sum(g.score(state, p) for g in board.objectives[team].values())
