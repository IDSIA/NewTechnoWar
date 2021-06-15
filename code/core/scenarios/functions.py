from typing import Tuple
import numpy as np

from core.const import RED, BLUE
from core.figures import Figure, stat
from core.game.board import GameBoard
from core.game.goals import GoalEliminateOpponent, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.game.state import GameState
from core.game.terrain import TERRAIN_TYPE
from core.scenarios.utils import fillLine, parse_slice
from core.templates import TMPL_BOARDS, TMPL_SCENARIOS, TMPL_FIGURES, setupWeapons, buildFigure


def parseBoard(name: str) -> GameBoard:
    bData = TMPL_BOARDS[name]
    shape = tuple(bData['shape'])
    board = GameBoard(shape, name)

    terrain = np.full(shape, TERRAIN_TYPE[bData['default']].level, dtype='uint8')

    for tName, tData in bData['terrain'].items():
        level = TERRAIN_TYPE[tName].level
        for elem in tData:
            if 'line' in elem:
                e = elem['line']
                fillLine(terrain, (e[0], e[1]), (e[2], e[3]), level)
            if 'region' in elem:
                start, end = elem['region'].split(',')
                terrain[parse_slice(start), parse_slice(end)] = level
            if 'row_alternate' in elem:
                low, high = elem['row_alternate']
                for i in range(board.shape[0]):
                    j = low if i % 2 == 0 else high
                    terrain[i, j] = level

    board.addTerrain(terrain)

    return board


def addPlacement(board: GameBoard, state: GameState, team: str, template: dict) -> None:
    """Add a placement zone to a state for the given team, given the correct template."""
    placement_zone = np.zeros(board.shape, dtype='uint8')
    for elem in template[team]['placement']:
        if 'region' in elem:
            start, end = elem['region'].split(',')
            placement_zone[parse_slice(start), parse_slice(end)] = 1

    state.addPlacementZone(team, placement_zone)


def addObjectives(board: GameBoard, team: str, objective: str, value) -> None:
    """Add an objective for a given team to the board using the given values."""
    other = BLUE if team == RED else RED
    obj = None
    if objective == 'eliminate_opponent':
        obj = GoalEliminateOpponent(team, other)
    if objective == 'reach_point':
        value = [tuple(w) for w in value]
        obj = GoalReachPoint(team, board.shape, value)
    if objective == 'defend_point':
        value = [tuple(w) for w in value]
        obj = GoalDefendPoint(team, other, board.shape, value)
    if objective == 'max_turn':
        obj = GoalMaxTurn(team, value)
    if obj:
        board.addObjectives(obj)


def addFigure(state: GameState, team: str, fName: str, fData: dict) -> None:
    """
    Add figures to a state for the given team, if needed add the color scheme, and also add the loaded units if there
    are any.
    """
    # setup main figure
    s = stat(fData['status']) if 'status' in fData else stat('NO_EFFECT')
    figure: Figure = buildFigure(fData['type'], fData['position'], team, fName, s)

    # setup colors
    color = fData.get('color', None)
    if color:
        state.addChoice(team, color, figure)
    else:
        state.addFigure(figure)

    for x in fData.get('loaded', []):
        # parse loaded figures
        for lName, lData in x.items():
            # setup loaded figure
            lt = TMPL_FIGURES[lData['type']]
            lFigure = Figure(fData['position'], lName, team, lt['kind'])

            # add parameters to loaded figure
            for lk, lv in lt.items():
                if lk == 'weapons':
                    setupWeapons(lFigure, lv)
                else:
                    setattr(lFigure, lk, lv)

            if color:
                state.addChoice(team, color, lFigure)
            else:
                state.addFigure(lFigure)

            figure.transportLoad(lFigure)


def buildScenario(name: str) -> Tuple[GameBoard, GameState]:
    """Build the scenario associated with the given name from the loaded templates."""
    template = TMPL_SCENARIOS[name]

    board: GameBoard = parseBoard(template['map'])
    state: GameState = GameState(board.shape, name)

    if 'turn' in template:
        state.turn = template['turn'] - 2  # turns are 0-based and there is 1 initialization update

    for team in [RED, BLUE]:
        if 'placement' in template[team]:
            addPlacement(board, state, team, template)

        if 'objectives' in template[team]:
            for o, v in template[team]['objectives'].items():
                addObjectives(board, team, o, v)

        if 'figures' in template[team]:
            for f in template[team]['figures']:
                addFigure(state, team, f, template[team]['figures'][f])

    return board, state
