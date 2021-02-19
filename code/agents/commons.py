from core.game import GameBoard, GameState, GoalParams


def stateScore(team: str, params: GoalParams, board: GameBoard, state: GameState) -> float:
    """Calculates the score of a state based on the objectives assigned to the given team."""
    goals = board.getObjectives(team)
    return sum([goal.score(state, params) for goal in goals])
