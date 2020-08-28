import unittest

from core import RED, BLUE
from core.figures import Infantry
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState


class TestFigures(unittest.TestCase):

    def setUp(self):
        shape = (16, 16)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.inf_1 = Infantry((5, 11), RED)
        self.inf_2 = Infantry((7, 12), RED)

        self.target_1 = Infantry((3, 13), BLUE)
        self.target_2 = Infantry((5, 13), BLUE)
        self.target_3 = Infantry((7, 13), BLUE)
        self.target_4 = Infantry((9, 13), BLUE)

        self.state.addFigure(
            self.inf_1,
            self.inf_2,
            self.target_1,
            self.target_2,
            self.target_3,
            self.target_4,
        )

        self.gm = GameManager()

    def testAttackAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        a1 = self.gm.actionAttack(self.board, self.state, self.inf_1, self.target_1, self.inf_1.weapons['AR'])
        r1 = self.gm.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        r2 = self.gm.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        self.gm.step(self.board, self.state, a1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can be both activated and responded
        self.gm.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        self.gm.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

    def testMoveAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        m1 = self.gm.actionMove(self.board, self.inf_1, destination=(5, 12))
        r1 = self.gm.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        m2 = self.gm.actionMove(self.board, self.inf_2, destination=(8, 12))
        r2 = self.gm.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        self.gm.step(self.board, self.state, m1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can responded after move
        self.gm.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        self.gm.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

        # check that unit can move after response
        self.gm.step(self.board, self.state, m2)

        self.assertTrue(self.inf_2.activated, 'unit should be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

    def testPassAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        p1 = self.gm.actionPass(self.inf_1)
        r1 = self.gm.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        p2 = self.gm.actionPass(self.inf_2)
        r2 = self.gm.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        self.gm.step(self.board, self.state, p1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can responded after move
        self.gm.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        self.gm.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

        # check that unit can move after response
        self.gm.step(self.board, self.state, p2)

        self.assertTrue(self.inf_2.activated, 'unit should be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')


if __name__ == '__main__':
    unittest.main()
