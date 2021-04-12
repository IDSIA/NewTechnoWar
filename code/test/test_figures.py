import unittest

from core.const import RED, BLUE
from core.figures import buildFigure
from core.game import GameBoard, GameState, GameManager
from core.utils.coordinates import Hex

GM: GameManager = GameManager()


class TestFigures(unittest.TestCase):

    def setUp(self):
        shape = (16, 16)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.inf_1 = buildFigure('Infantry', (5, 11), RED)
        self.inf_2 = buildFigure('Infantry', (7, 12), RED)

        self.target_1 = buildFigure('Infantry', (3, 13), BLUE)
        self.target_2 = buildFigure('Infantry', (5, 13), BLUE)
        self.target_3 = buildFigure('Infantry', (7, 13), BLUE)
        self.target_4 = buildFigure('Infantry', (9, 13), BLUE)

        self.state.addFigure(
            self.inf_1,
            self.inf_2,
            self.target_1,
            self.target_2,
            self.target_3,
            self.target_4,
        )

    def testAttackAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        a1 = GM.actionAttack(self.board, self.state, self.inf_1, self.target_1, self.inf_1.weapons['AR'])
        r1 = GM.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        r2 = GM.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        GM.step(self.board, self.state, a1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can be both activated and responded
        GM.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        GM.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

    def testMoveAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        dst1 = Hex(5, 12).cube()
        dst2 = Hex(8, 12).cube()

        m1 = GM.actionMove(self.board, self.state, self.inf_1, destination=dst1)
        r1 = GM.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        m2 = GM.actionMove(self.board, self.state, self.inf_2, destination=dst2)
        r2 = GM.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        GM.step(self.board, self.state, m1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can responded after move
        GM.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        GM.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

        # check that unit can move after response
        GM.step(self.board, self.state, m2)

        self.assertTrue(self.inf_2.activated, 'unit should be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

    def testPassAndResponse(self):
        # check default status
        self.assertFalse(self.inf_1.activated)
        self.assertFalse(self.inf_1.responded)
        self.assertFalse(self.inf_2.activated)
        self.assertFalse(self.inf_2.responded)

        p1 = GM.actionPassFigure(self.inf_1)
        r1 = GM.actionRespond(self.board, self.state, self.inf_1, self.target_2, self.inf_1.weapons['AR'])
        p2 = GM.actionPassFigure(self.inf_2)
        r2 = GM.actionRespond(self.board, self.state, self.inf_2, self.target_3, self.inf_1.weapons['AR'])

        # check that attack activate unit
        GM.step(self.board, self.state, p1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertFalse(self.inf_1.responded, 'unit should not have responded')

        # check that unit can responded after move
        GM.step(self.board, self.state, r1)

        self.assertTrue(self.inf_1.activated, 'unit should be activated')
        self.assertTrue(self.inf_1.responded, 'unit should have responded')

        # check that response does not activate the unit
        GM.step(self.board, self.state, r2)

        self.assertFalse(self.inf_2.activated, 'unit should not be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')

        # check that unit can move after response
        GM.step(self.board, self.state, p2)

        self.assertTrue(self.inf_2.activated, 'unit should be activated')
        self.assertTrue(self.inf_2.responded, 'unit should have responded')


if __name__ == '__main__':
    unittest.main()
