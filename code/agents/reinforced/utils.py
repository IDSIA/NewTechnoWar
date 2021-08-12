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


def calculateValidMoves(board, state, team, moveType, reduced=False):
    allValidActions = []

    gm = GameManager()

    if moveType == "Action":

        print('moving', team, 'move: A;')  # , 'last action:', state.lastAction, "|", lastAction)

        for figure in state.getFiguresCanBeActivated(team):  # TODO: team

            actions = [gm.actionPassFigure(figure)] + \
                gm.buildAttacks(board, state, figure) + \
                gm.buildMovements(board, state, figure)

            allValidActions += actions

    elif moveType == "Response":

        print('moving', team, 'move: R;')  # , 'last action:', state.lastAction, "|", lastAction)

        for figure in state.getFiguresCanBeActivated(team):  # TODO: team

            actions = gm.buildResponses(board, state, figure)
            allValidActions += actions

        allValidActions += [gm.actionNoResponse(team)]

    if reduced:
        return calculateValidMovesReduced(board, state, team, moveType, allValidActions)

    return allValidActions


def calculateValidMovesReduced(board, state, team, moveType, allValidActions):
    # TODO: filter the actions to just some more useful actions
    reducedActions = []

    for action in allValidActions:
        reducedActions.append(action)

    return reducedActions
