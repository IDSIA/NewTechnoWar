import unittest

from agents import AgentDummy
from agents.matchmanager import MatchManager
from core import GM
from core.const import RED, BLUE
from core.figures import Tank, Infantry
from core.figures.status import IN_MOTION
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube, Cube, cube_to_hex


class TestMovementAction(unittest.TestCase):

    def setUp(self):
        red = AgentDummy(RED)
        blue = AgentDummy(BLUE)

        shape = (16, 16)
        board = GameBoard(shape)
        state = GameState(shape)

        self.tank = Tank((8, 8), RED)
        state.addFigure(self.tank)

        # initialization
        self.mm = MatchManager('', red, blue, board, state)

    def testMoveToDestination(self):
        dst = (4, 4)
        board = self.mm.board
        state = self.mm.state
        move = GM.actionMove(board, self.tank, destination=dst)

        GM.step(board, state, move)

        self.assertEqual(state.getFiguresByPos(move.team, move.destination)[0], self.tank,
                         'figure in the wrong position')
        self.assertEqual(self.tank.stat, IN_MOTION, 'figure should be in motion')
        self.assertEqual(self.tank.position, to_cube(dst), 'figure not at the correct destination')

    def testActivateMoveToDestination(self):
        dst = (4, 4)
        board = self.mm.board
        state = self.mm.state
        move = GM.actionMove(board, self.tank, destination=dst)

        state1, _ = GM.activate(board, state, move)
        self.assertNotEqual(hash(state1), hash(state), 'state1 and state0 are the same, should be different!')
        self.assertNotEqual(state.getFigure(move).position, state1.getFigure(move).position,
                            'figure is in teh same location for both state0 and state1!')

        state2, _ = GM.activate(board, state, move)
        self.assertNotEqual(hash(state2), hash(state), 'state2 and state0 are the same, should be different!')
        self.assertEqual(state1.getFigure(move).position, state2.getFigure(move).position,
                         'state1 and state2 have different end location')

        state3, _ = GM.activate(board, state, move)
        self.assertNotEqual(hash(state3), hash(state), 'state3 and state0 are the same, should be different!')
        self.assertEqual(state1.getFigure(move).position, state3.getFigure(move).position,
                         'state1 and state3 have different end location')
        self.assertEqual(state2.getFigure(move).position, state3.getFigure(move).position,
                         'state2 and state3 have different end location')

    def testMoveWithTransport(self):
        board = self.mm.board
        state = self.mm.state

        inf1 = Infantry((7, 7), RED, 'Inf1')
        inf2 = Infantry((7, 8), RED, 'Inf2')
        inf3 = Infantry((7, 9), RED, 'Inf3')

        # add infantry units
        state.addFigure(inf1)
        state.addFigure(inf2)
        state.addFigure(inf3)

        # load 2 units
        load1 = GM.actionLoadInto(board, inf1, self.tank)
        load2 = GM.actionLoadInto(board, inf2, self.tank)
        load3 = GM.actionLoadInto(board, inf3, self.tank)

        GM.step(board, state, load1)
        GM.step(board, state, load2)

        # load a third unit: cannot do that!
        self.assertRaises(ValueError, GM.step, board, state, load3)

        self.assertEqual(inf1.position, self.tank.position)
        self.assertEqual(inf2.position, self.tank.position)
        self.assertNotEqual(inf3.position, self.tank.position)

        # move figure in same position of tank
        move = GM.actionMove(board, inf3, destination=self.tank.position)
        GM.step(board, state, move)

        figures = state.getFiguresByPos(RED, self.tank.position)
        self.assertEqual(len(figures), 4, 'not all figures are in the same position')
        self.assertEqual(inf1.transported_by, self.tank.index, 'Inf1 not in transporter')
        self.assertEqual(inf2.transported_by, self.tank.index, 'Inf2 not in transporter')
        self.assertEqual(inf3.transported_by, -1, 'Inf3 is in transporter')

        # move tank
        move = GM.actionMove(board, self.tank, destination=(8, 2))
        GM.step(board, state, move)

        # figures moves along with tank
        self.assertEqual(inf1.position, self.tank.position, 'Inf1 not moved with transporter')
        self.assertEqual(inf2.position, self.tank.position, 'Inf2 not moved with transporter')
        self.assertEqual(len(self.tank.transporting), 2, 'Transporter not transporting all units')

        self.assertGreater(inf1.transported_by, -1)

        # unload 1 figure
        move = GM.actionMove(board, inf1, destination=(8, 4))
        GM.step(board, state, move)

        self.assertEqual(len(self.tank.transporting), 1, 'transporter has less units than expected')
        self.assertNotEqual(inf1.position, self.tank.position, 'Inf1 has not been moved together with transporter')

    def testMoveInsideShape(self):
        board = self.mm.board
        state = self.mm.state
        figure = self.tank

        # top left
        state.moveFigure(figure, dst=to_cube((0, 0)))

        moves = GM.buildMovements(board, state, figure)

        for move in moves:
            d: Cube = move.destination
            x, y = cube_to_hex(d)
            self.assertGreaterEqual(x, 0, f'moves outside of map limits: ({x},{y})')
            self.assertGreaterEqual(y, 0, f'moves outside of map limits: ({x},{y})')

        # bottom right
        state.moveFigure(figure, dst=to_cube((15, 15)))

        moves = GM.buildMovements(board, state, figure)

        for move in moves:
            d: Cube = move.destination
            x, y = cube_to_hex(d)
            self.assertLess(x, 16, f'moves outside of map limits: ({x},{y})')
            self.assertLess(y, 16, f'moves outside of map limits: ({x},{y})')

    def testMoveOutsideShape(self):
        board = self.mm.board
        state = self.mm.state
        figure = self.tank

        # outside of map
        state.moveFigure(figure, dst=to_cube((-1, -1)))

        moves = GM.buildMovements(board, state, figure)

        self.assertEqual(len(moves), 0, 'moves outside of the map!')


if __name__ == '__main__':
    unittest.main()
