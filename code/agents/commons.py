from core.game import GameBoard, GameState, GoalParams


def stateScore(team: str, params: GoalParams, board: GameBoard, state: GameState) -> float:
    """
    Calculates the score of a state based on the objectives assigned to the given team. The given "params" are used to
    assign a score to each goal in the GameBoard based on the given GameState.

    :param team:        team that performs the action
    :param params:      GoalParams given to the agent
    :param board:       board of the game
    :param state:       current state to evaluate
    :return: the score associate to the current state based on the given params
    """
    goals = board.getObjectives(team)
    return sum([goal.score(state, params) for goal in goals])
