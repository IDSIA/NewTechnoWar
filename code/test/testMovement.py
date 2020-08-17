import unittest

from agents.matchmanager import MatchManager
from agents.players import PlayerDummy
from core import RED, BLUE
from core.actions import LoadInto, Move
from core.figures import Tank, Infantry
from core.figures.status import IN_MOTION
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube


class TestMovementAction(unittest.TestCase):

    def setUp(self):
        red = PlayerDummy(RED)
        blue = PlayerDummy(BLUE)

        shape = (16, 16)
        board = GameBoard(shape)
        state = GameState(shape)

        self.tank = Tank((8, 8), RED)
        state.addFigure(self.tank)

        # initialization
        self.mm = MatchManager('', board, state, red, blue)
        # self.mm.step()

        # compute reachable area
        self.movements = self.mm.gm.buildMovements(board, state, self.tank)

    def testMoveToDestination(self):
        board = self.mm.board
        state = self.mm.state
        move = self.movements[0]

        self.mm.gm.step(board, state, move)

        self.assertEqual(state.getFiguresByPos(move.team, move.destination)[0], self.tank,
                         'figure in the wrong position')
        self.assertEqual(self.tank.stat, IN_MOTION, 'figure should be in motion')

    def testStepMoveToDestination(self):
        board = self.mm.board
        state = self.mm.state
        move = self.movements[0]

        state1, _ = self.mm.gm.activate(board, state, move)
        self.assertNotEqual(hash(state1), hash(state), 'state1 and state0 are the same, should be different!')

        state2, _ = self.mm.gm.activate(board, state, move)
        self.assertNotEqual(hash(state2), hash(state), 'state2 and state0 are the same, should be different!')
        self.assertEqual(state1.getFigure(move).position, state2.getFigure(move).position,
                         'state1 and state2 have different end location')

        state3, _ = self.mm.gm.activate(board, state, move)
        self.assertNotEqual(hash(state3), hash(state), 'state3 and state0 are the same, should be different!')
        self.assertEqual(state1.getFigure(move).position, state3.getFigure(move).position,
                         'state1 and state3 have different end location')
        self.assertEqual(state2.getFigure(move).position, state3.getFigure(move).position,
                         'state2 and state3 have different end location')

    def testMoveWithTransport(self):
        board = self.mm.board
        state = self.mm.state

        inf1 = Infantry((7, 4), RED, 'Inf1')
        inf2 = Infantry((7, 4), RED, 'Inf2')
        inf3 = Infantry((7, 4), RED, 'Inf3')

        # add infantry units
        state.addFigure(inf1)
        state.addFigure(inf2)
        state.addFigure(inf3)

        # load 2 units
        self.mm.gm.step(board, state, LoadInto(RED, inf1, [self.tank.position], self.tank))
        self.mm.gm.step(board, state, LoadInto(RED, inf2, [self.tank.position], self.tank))

        # load a third unit: cannot do that!
        self.assertRaises(ValueError, self.mm.gm.step, board, state,
                          LoadInto(RED, inf3, [self.tank.position], self.tank))

        self.assertEqual(inf1.position, self.tank.position)
        self.assertEqual(inf2.position, self.tank.position)
        self.assertNotEqual(inf3.position, self.tank.position)

        # move tank
        self.mm.gm.step(board, state, Move(RED, self.tank, [to_cube((8, 1))]))

        # figures moves along with tank
        self.assertEqual(inf1.position, self.tank.position)
        self.assertEqual(inf2.position, self.tank.position)

        self.assertGreater(inf1.transported_by, -1)

        # unload 1 figure
        self.mm.gm.step(board, state, Move(RED, inf1, [to_cube((8, 4))]))

        self.assertEqual(len(self.tank.transporting), 1)
        self.assertNotEqual(inf1.position, self.tank.position)


if __name__ == '__main__':
    unittest.main()
