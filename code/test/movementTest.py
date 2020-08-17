from agents.matchmanager import MatchManager
from agents.players import PlayerDummy
from core import RED, BLUE
from core.figures import Tank
from core.game.board import GameBoard
from core.game.state import GameState

red = PlayerDummy(RED)
blue = PlayerDummy(BLUE)

shape = (16, 16)
board = GameBoard(shape)
state = GameState(shape)

tank = Tank((8, 8), RED)
state.addFigure(tank)

# initialization
mm = MatchManager('', board, state, red, blue)
mm.step()

# compute reachable area
movements = mm.gm.buildMovements(board, state, tank)

# perform move action
m = movements[0]

state1, _ = mm.gm.activate(board, state, m)
assert hash(state1) != hash(state)

state2, _ = mm.gm.activate(board, state, m)
assert hash(state2) != hash(state)
assert state1.getFigure(m).position == state2.getFigure(m).position

state3, _ = mm.gm.activate(board, state, m)
assert hash(state3) != hash(state)
assert state1.getFigure(m).position == state3.getFigure(m).position
assert state2.getFigure(m).position == state3.getFigure(m).position
