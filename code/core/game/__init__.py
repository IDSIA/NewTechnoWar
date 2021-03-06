__all__ = [
    "GameBoard", "GameState",
    "GameManager",
    "GoalParams", "Goal", "GoalEliminateOpponent", "GoalReachPoint", "GoalDefendPoint", "GoalMaxTurn", "goalAchieved", "goalScore"
    "GOAL_KEY_LIST",
    "hitScoreCalculator",
    "Terrain", "TERRAIN_TYPE", "TYPE_TERRAIN",
    "vectorState", "vectorStateInfo",
    "MAX_SMOKE", "CUTOFF_RANGE", "MAX_UNITS_PER_TEAM",
    "Outcome",
]

from core.game.board import GameBoard
from core.game.goals import Goal, GoalEliminateOpponent, GoalReachPoint, GoalDefendPoint, GoalMaxTurn, goalAchieved, GoalParams, goalScore
from core.game.manager import GameManager
from core.game.outcome import Outcome
from core.game.scores import hitScoreCalculator
from core.game.state import GameState, vectorState, vectorStateInfo
from core.game.static import MAX_SMOKE, CUTOFF_RANGE, MAX_UNITS_PER_TEAM
from core.game.terrain import Terrain, TERRAIN_TYPE, TYPE_TERRAIN

GOAL_KEY_LIST = [
    GoalEliminateOpponent.__name__,
    GoalReachPoint.__name__,
    GoalDefendPoint.__name__,
    GoalMaxTurn.__name__
]
