import unittest

from agents.matchmanager import MatchManager
from agents.players import PlayerDummy
from core import RED, BLUE
from core.figures import Tank, Infantry
from core.game.board import GameBoard
from core.game.state import GameState


class TestAttack(unittest.TestCase):

    def setUp(self):
        red = PlayerDummy(RED)
        blue = PlayerDummy(BLUE)

        shape = (16, 16)
        board = GameBoard(shape)
        state = GameState(shape)

        self.red_tank = Tank((0, 6), RED)
        self.red_inf = Infantry((0, 12), RED)

        self.blue_tank = Tank((15, 12), BLUE)
        self.blue_inf = Infantry((15, 12), BLUE)

        state.addFigure(self.red_tank)
        state.addFigure(self.red_inf)
        state.addFigure(self.blue_tank)
        state.addFigure(self.blue_inf)

        # initialization
        self.mm = MatchManager('', board, state, red, blue)

    def testAttack(self):
        board = self.mm.board
        state = self.mm.state
        attack = self.mm.gm.actionAttack(board, state, self.red_tank, self.blue_tank, self.red_tank.weapons['CA'])

        target = state.getTarget(attack)
        weapon = state.getWeapon(attack)

        o = self.mm.gm.step(board, state, attack)

        self.assertTrue(o['success'], 'failed to attack target')
        self.assertTrue(target.killed, 'target still alive')

        self.assertEqual(target.hp, target.hp_max - 1, 'no damage to the target')
        self.assertEqual(weapon.ammo, weapon.ammo_max - 1, 'shell not fired')

    def testActivateAttack(self):
        board = self.mm.board
        state = self.mm.state
        attack = self.mm.gm.actionAttack(board, state, self.red_inf, self.blue_inf, self.red_tank.weapons['AR'])

        t0 = state.getTarget(attack)
        w0 = state.getWeapon(attack)

        s1, o = self.mm.gm.activate(board, state, attack)
        s2, o = self.mm.gm.activate(board, state, attack)

        self.assertNotEqual(hash(state), hash(s1), 'state1 and state0 are the same')
        self.assertNotEqual(hash(state), hash(s2), 'state2 and state0 are the same')

        t1 = s1.getTarget(attack)
        w1 = s1.getWeapon(attack)

        self.assertNotEqual(t0.killed, t1.killed, 'both target have the same status')
        self.assertFalse(t0.killed, 'target for state0 has been killed')
        self.assertTrue(t1.killed, 'target for state1 is still alive')

        self.assertEqual(w0.ammo - 1, w1.ammo, 'shots fired in the wrong state')

    def testShootingGround(self):
        board = self.mm.board
        state = self.mm.state


if __name__ == '__main__':
    unittest.main()
