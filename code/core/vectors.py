from core.actions import ACTION_KEY_LIST, Action, Move, Attack, Response
from core.figures import WEAPON_KEY_LIST
from core.game import GameBoard, GameState
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
    raise NotImplemented()


def vectorBoard(board: GameBoard, state: GameState) -> tuple:
    # TODO: add features that are an interaction of board and state:
    #       - distance from goals
    #       - LOS/LOF blocked
    #       - distance to cover (forest, building)
    raise NotImplemented()
