from core.actions import ACTION_KEY_LIST, Action, Move, Attack, Response
from core.const import RED, BLUE
from core.figures import WEAPON_KEY_LIST, FigureType
from core.game import GameBoard, GameState, GOAL_KEY_LIST, GoalParams, GameManager, goalAchieved
from core.game.static import MAX_UNITS_PER_TEAM


def vectorActionInfo() -> tuple:
    info = []
    for i in range(MAX_UNITS_PER_TEAM):
        info.append(f'action_figure_{i}')

    info.append('action_team')

    for a in ACTION_KEY_LIST:
        info.append(f'action_type_{a}')

    info.append('action_destination_x')
    info.append('action_destination_y')
    info.append('action_destination_z')
    info.append('action_path')

    for i in range(MAX_UNITS_PER_TEAM):
        info.append(f'action_guard_{i}')

    info.append('action_lof')
    info.append('action_los')

    for i in range(MAX_UNITS_PER_TEAM):
        info.append(f'action_target_{i}')

    for w in WEAPON_KEY_LIST:
        info.append(f'action_weapon_{w}')

    info.append('response')

    return tuple(info)


def vectorAction(action: Action) -> tuple:
    if not action:
        return tuple([None] * len(vectorActionInfo()))

    action_type = [False] * len(ACTION_KEY_LIST)
    action_type[ACTION_KEY_LIST.index(action.__class__.__name__)] = True

    action_team = action.team

    response = False
    action_figure_index = [False] * MAX_UNITS_PER_TEAM
    action_destination_x = 0
    action_destination_y = 0
    action_destination_z = 0
    action_path = 0
    action_guard_index = [False] * MAX_UNITS_PER_TEAM
    action_lof = 0
    action_los = 0
    action_target_index = [False] * MAX_UNITS_PER_TEAM
    action_weapon_id = [False] * len(WEAPON_KEY_LIST)

    if isinstance(action, Move):
        action_figure_index[action.figure_id] = True
        action_destination_x = action.destination.x
        action_destination_y = action.destination.y
        action_destination_z = action.destination.z
        action_path = len(action.path)

    if isinstance(action, Attack):
        action_figure_index[action.figure_id] = True
        action_guard_index[action.guard_id] = True
        action_lof = len(action.lof)  # direct line of fire on target (from the attacker)
        action_los = len(action.los)  # direct line of sight on target (from who can see it)
        action_target_index[action.target_id] = True
        action_weapon_id[WEAPON_KEY_LIST.index(action.weapon_id)] = True

    if isinstance(action, Response):
        response = True

    data = list()
    data += action_figure_index
    data.append(action_team)
    data += action_type
    data.append(action_destination_x)
    data.append(action_destination_y)
    data.append(action_destination_z)
    data.append(action_path)
    data += action_guard_index
    data.append(action_lof)
    data.append(action_los)
    data += action_target_index
    data += action_weapon_id
    data.append(response)

    return tuple(data)


def vectorBoardInfo() -> tuple:
    # TODO: add header for features that are board-dependent
    info = []

    # LOS/LOF check
    for team in [RED, BLUE]:
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                if i != j:
                    info.append(f'{team}_LOS_{i}_{j}_valid')

    info += [
        'goal_params_unit_team_lost',
        'goal_params_unit_team_alive',
        'goal_params_unit_enemy_killed',
        'goal_params_unit_enemy_alive',
        'goal_params_reach_team_near',
        'goal_params_defend_team_near',
        'goal_params_defend_enemy_near',
        'goal_params_wait_for_turn',
    ]

    for team in [RED, BLUE]:
        for goal in GOAL_KEY_LIST:
            info.append(f'{team}_goal_{goal}_score')
            info.append(f'{team}_goal_{goal}_check')

    info += [
        'goal_achieved',
        'action_move_destination_protection_level',
        'action_move_destination_move_cost_infantry',
        'action_move_destination_move_cost_vehicle'
    ]

    return tuple(info)


def vectorBoard(board: GameBoard, state: GameState, action: Action = None, params: GoalParams = None) -> tuple:
    # TODO: add features that are an interaction of board and state:
    #       - distance from goals
    #       - distance to cover (forest, building)

    data = []

    # LOS/LOF check
    for teams in [(RED, BLUE), (BLUE, RED)]:
        team, other = teams
        for i in range(MAX_UNITS_PER_TEAM):
            for j in range(MAX_UNITS_PER_TEAM):
                if i != j:
                    if i < len(state.figures[team]) and j < len(state.figures[team]):
                        line: list = state.figuresDistance.get(team)[j][i]
                        data.append(GameManager.checkLine(board, state, line))
                    else:
                        data.append(None)

    # goals parameter (static for the whole game) TODO: and if we made them dynamic?!
    if params:
        data += [
            params.unit_team_lost,
            params.unit_team_alive,
            params.unit_enemy_killed,
            params.unit_enemy_alive,
            params.reach_team_near,
            params.defend_team_near,
            params.defend_enemy_near,
            params.wait_for_turn
        ]
    else:
        params = GoalParams()
        data += [None] * 8

    # info on the goals
    for team in [RED, BLUE]:
        objectives = board.objectives[team]

        for goal in GOAL_KEY_LIST:
            if goal in objectives:
                obj = objectives[goal]
                data.append(obj.score(state, params))
                data.append(obj.check(state))
            else:
                data.append(None)
                data.append(None)

    data.append(goalAchieved(board, state))

    # extra info from action
    if action and isinstance(action, Move):
        data.append(board.getProtectionLevel(action.destination))
        data.append(board.getMovementCost(action.destination, FigureType.INFANTRY))
        data.append(board.getMovementCost(action.destination, FigureType.VEHICLE))
    else:
        data.append(None)
        data.append(None)
        data.append(None)

    return tuple(data)
