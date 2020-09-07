import unittest

from core import GM
from core.const import RED, BLUE
from core.figures import Tank, Infantry
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube


class TestAttackAction(unittest.TestCase):

    def setUp(self):
        shape = (16, 16)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.red_tank = Tank((0, 6), RED)
        self.red_inf = Infantry((0, 12), RED)

        self.blue_tank = Tank((15, 6), BLUE)
        self.blue_inf = Infantry((15, 12), BLUE)

        self.state.addFigure(
            self.red_tank,
            self.red_inf,
            self.blue_tank,
            self.blue_inf
        )

    def testAttack(self):
        attack = GM.actionAttack(
            self.board, self.state, self.red_tank, self.blue_tank, self.red_tank.weapons['CA']
        )

        target = self.state.getTarget(attack)
        weapon = self.state.getWeapon(attack)

        o = GM.step(self.board, self.state, attack, True)

        self.assertTrue(o['success'], 'failed to attack target')
        self.assertTrue(target.killed, 'target still alive')

        self.assertEqual(target.hp, target.hp_max - 1, 'no damage to the target')
        self.assertEqual(weapon.ammo, weapon.ammo_max - 1, 'shell not fired')

    def testActivateAttack(self):
        atk = GM.actionAttack(self.board, self.state, self.red_tank, self.blue_tank, self.red_tank.weapons['CA'])

        t0 = self.state.getTarget(atk)
        w0 = self.state.getWeapon(atk)

        s1, o = GM.activate(self.board, self.state, atk, True)
        s2, o = GM.activate(self.board, self.state, atk, True)

        self.assertNotEqual(hash(self.state), hash(s1), 'state1 and state0 are the same')
        self.assertNotEqual(hash(self.state), hash(s2), 'state2 and state0 are the same')

        t1 = s1.getTarget(atk)
        w1 = s1.getWeapon(atk)

        self.assertNotEqual(t0.killed, t1.killed, 'both target have the same status')
        self.assertFalse(t0.killed, 'target for state0 has been killed')
        self.assertTrue(t1.killed, 'target for state1 is still alive')

        self.assertEqual(w0.ammo - 1, w1.ammo, 'shots fired in the wrong state')

    def testShootingGround(self):
        ground = (2, 6)
        attack = GM.actionAttackGround(self.red_tank, to_cube(ground), self.red_tank.weapons['SM'])

        GM.step(self.board, self.state, attack)

        self.assertEqual(self.state.smoke.max(), 2, 'cloud with wrong value')
        self.assertEqual(self.state.smoke.sum(), 6, 'not enough hex have cloud')

        GM.update(self.state)
        self.assertEqual(self.state.smoke.max(), 1, 'cloud decay not working')

        atk = GM.actionAttack(self.board, self.state, self.blue_tank, self.red_tank, self.red_tank.weapons['CA'])
        outcome = GM.step(self.board, self.state, atk)

        self.assertGreaterEqual(outcome['DEF'], 18, 'smoke defense not active')

        GM.update(self.state)
        GM.update(self.state)
        self.assertEqual(self.state.smoke.max(), 0, 'cloud not disappearing correctly')

    def testDisableWeapon(self):
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
