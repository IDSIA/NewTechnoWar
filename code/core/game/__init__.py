__all__ = [
    "GameBoard", "GameState",
    "GameManager",
    "GoalParams", "Goal", "GoalEliminateOpponent", "GoalReachPoint", "GoalDefendPoint", "GoalMaxTurn", "goalAchieved",
    "GOAL_KEY_LIST",
    "hitScoreCalculator",
    "Terrain", "TERRAIN_TYPE",
    "vectorState", "vectorStateInfo",
]

from core.game.board import GameBoard
from core.game.goals import Goal, GoalEliminateOpponent, GoalReachPoint, GoalDefendPoint, GoalMaxTurn, goalAchieved, \
    GoalParams
from core.game.manager import GameManager
from core.game.scores import hitScoreCalculator
from core.game.state import GameState, vectorState, vectorStateInfo
from core.game.static import MAX_SMOKE, CUTOFF_RANGE
from core.game.terrain import Terrain, TERRAIN_TYPE

GOAL_KEY_LIST = [
    GoalEliminateOpponent.__name__, GoalReachPoint.__name__, GoalDefendPoint.__name__, GoalMaxTurn.__name__
]
