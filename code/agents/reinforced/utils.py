from core.actions import MoveLoadInto


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
