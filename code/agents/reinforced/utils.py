from core.actions.movements import MoveLoadInto
from core.game.manager import GameManager


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


def calculateValidMoves(board, state, team, moveType, reduced=False):  # TODO: set the reduced parameters to True to reduce the number of movements actions
    allValidActions = []

    gm = GameManager()

    if moveType == "Action":

        print('moving', team, 'move: A;')  # , 'last action:', state.lastAction, "|", lastAction)

        for figure in state.getFiguresCanBeActivated(team):  # TODO: team

            actions = [gm.actionPassFigure(figure)] + \
                gm.buildAttacks(board, state, figure)

            if reduced:
                actions += limitMovements(board, state, gm.buildMovements(board, state, figure))
            else:
                actions += gm.buildMovements(board, state, figure)

            allValidActions += actions

    elif moveType == "Response":

        print('moving', team, 'move: R;')  # , 'last action:', state.lastAction, "|", lastAction)

        for figure in state.getFiguresCanBeActivated(team):  # TODO: team

            actions = gm.buildResponses(board, state, figure)
            allValidActions += actions

        allValidActions += [gm.actionNoResponse(team)]

    return allValidActions


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
