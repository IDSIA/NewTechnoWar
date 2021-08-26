from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam, AttackResponse, PassFigure, AttackGround, MoveLoadInto
from core.const import RED, BLUE

WEAPONS_INDICES: dict = {
    'AT': 0,
    'AR': 1,
    'CA': 2,
    'MT': 3,
    'GR': 4,
    'MG': 5,
    'SG': 6,
    'SR': 7
}


def calculateValidMoves(gm, board, state, team, move_type, reduced=False):  # TODO: set the reduced parameters to True to reduce the number of movements actions
    all_valid_actions = []

    if move_type == "Action":

        print('moving', team, 'move: A;')  # , 'last action:', state.lastAction, "|", lastAction)

        all_valid_actions = gm.buildActionsForTeam(board, state, team)

        # for figure in state.getFiguresCanBeActivated(team):  # TODO: team

        #     actions = [gm.actionPassFigure(figure)] + \
        #         gm.buildAttacks(board, state, figure)

        #     if reduced:
        #         actions += limitMovements(board, state, gm.buildMovements(board, state, figure))
        #     else:
        #         actions += gm.buildMovements(board, state, figure)

        #     all_valid_actions += actions

    elif move_type == "Response":

        print('moving', team, 'move: R;')  # , 'last action:', state.lastAction, "|", lastAction)

        all_valid_actions = gm.buildResponsesForTeam(board, state, team)

        # for figure in state.getFiguresCanBeActivated(team):  # TODO: team

        #     actions = gm.buildResponses(board, state, figure)
        #     all_valid_actions += actions

        # all_valid_actions += [gm.actionNoResponse(team)]

    return all_valid_actions


def actionIndexMapping(allValidActions, maxActionSize, maxMoveNoResponseSize, maxWeaponPerFigure, maxFigurePerScenario):
    # TODO: consider Wait actions if needed

    valid_indices = [0] * maxActionSize
    valid_actions = [None] * maxActionSize

    if allValidActions != []:

        for a in allValidActions:
            idx = -1

            if type(a) == AttackResponse or type(a) == Attack:

                figure_ind = a.figure_id
                target_ind = a.target_id

                weapon_ind = WEAPONS_INDICES[a.weapon_id]

                idx = (
                    maxMoveNoResponseSize +
                    weapon_ind +
                    target_ind * maxWeaponPerFigure +
                    figure_ind * maxWeaponPerFigure * maxFigurePerScenario
                )

            elif type(a) == NoResponse:

                idx = maxMoveNoResponseSize - 1

            elif type(a) == PassTeam:

                idx = maxMoveNoResponseSize

            else:

                if type(a) == PassFigure:
                    x = 0
                    y = 0

                # elif type(a) == Attack: # TODO: add weapons

                #     start_pos = a.position.tuple()
                #     end_pos = a.destination.tuple()

                #     x = end_pos[0] - start_pos[0]
                #     y = end_pos[1] - start_pos[1]

                # elif type(a) == AttackGround: # TODO: add weapons

                #     start_pos = a.position.tuple()
                #     end_pos = a.destination.tuple()

                #     x = end_pos[0] - start_pos[0]
                #     y = end_pos[1] - start_pos[1]

                elif type(a) == Move:

                    start_pos = a.position.tuple()
                    end_pos = a.destination.tuple()

                    x = end_pos[0] - start_pos[0]
                    y = end_pos[1] - start_pos[1]

                elif type(a) == MoveLoadInto:

                    start_pos = a.position.tuple()
                    end_pos = a.destination.tuple()

                    x = end_pos[0] - start_pos[0]
                    y = end_pos[1] - start_pos[1]

                figure_index = a.figure_id

                if x+y <= 0:
                    index_shift = ((x+y+(7+7))*(x+y+(7+7+1)))//2+y+7
                else:
                    index_shift = 224-(((x+y-(7+7))*(x+y-(7+7+1)))//2-y-7)

                idx = figure_index * 225 + index_shift

            valid_indices[idx] = 1
            valid_actions[idx] = a

    return valid_indices, valid_actions


def limitMovements(board, state, moves):
    # TODO: filter the actions to just some more useful actions
    min_neigh_sum = 2  # if greater than 0, consider all terrain that are not OPEN
    top_n = 10  # number of hex nearest the target to consider

    actions = []
    remaining = []

    for move in moves:
        dst = move.destination
        neighbor = dst.range(1)
        neighbor_tuples = [x.tuple() for x in neighbor]
        neighbor_sum = sum(board.terrain[x] for x in neighbor_tuples if 0 < x[0] < board.shape[0] and 0 < x[1] < board.shape[1])
        if neighbor_sum > min_neigh_sum:
            # consider hex that are adjacent to 'special' terrain
            actions.append(move)
        elif isinstance(move, MoveLoadInto):
            # consider load actions
            actions.append(move)
        else:
            # these hex will be limited by the top_n param respect to the distance to the nearest goal
            remaining.append(move)

    actions += sorted(remaining, key=lambda x: min([x.destination.distance(y) for y in board.getObjectiveMark()]))[:top_n]

    return actions


def mapTeamMoveIntoID(team, moveType):
    if team == RED and moveType == "Action":
        return 0
    elif team == RED and moveType == "Response":
        return 1
    elif team == BLUE and moveType == "Action":
        return 2
    elif team == BLUE and moveType == "Response":
        return 3
