from agents.matchmanager import MatchManager
from core import RED, BLUE

# initialization
mm: MatchManager = MatchManager('', 'scenarioTestBench', 'PlayerDummy', 'PlayerDummy')
mm.step()

gm = mm.gm
board = mm.board
state = mm.state

redTank = state.getFiguresByPos(RED, (2, 1))[0]
blueTank = state.getFiguresByPos(BLUE, (12, 12))[0]

# compute reachable area
movements = gm.buildMovements(board, state, BLUE, blueTank)

# perform move action
m = movements[0]

state1, outcome = gm.activate(board, state, m)
