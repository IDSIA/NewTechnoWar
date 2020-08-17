import unittest

from agents.matchmanager import MatchManager
from agents.players import PlayerDummy
from core import RED, BLUE
from core.figures import Tank
from core.game.board import GameBoard
from core.game.state import GameState


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
        self.mm.step()

        # compute reachable area
        self.movements = self.mm.gm.buildMovements(board, state, self.tank)

    def testMoveToDestination(self):
        board = self.mm.board
        state = self.mm.state
        move = self.movements[0]

        self.mm.gm.activate(board, state, move)

        self.assertEqual(state.getFiguresByPos(move.team, move.position)[0], self.tank, 'figure in the wrong position')

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


if __name__ == '__main__':
    unittest.main()
