import unittest

from core import RED, BLUE
from core.actions import Move
from core.figures import Tank, Infantry
from core.game.board import GameBoard
from core.game.goals import GoalMaxTurn, GoalReachPoint, GoalEliminateOpponent
from core.game.manager import GameManager
from core.game.state import GameState
from utils.coordinates import to_cube


class TestGoals(unittest.TestCase):

    def setUp(self):
        shape = (8, 8)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.gm = GameManager()

        self.blue_tank = Tank((6, 4), BLUE)
        self.red_tank = Tank((1, 4), RED)
        self.red_inf = Infantry((2, 4), RED)

        self.state.addFigure(self.red_tank, self.red_inf, self.blue_tank)

    def testEliminateOpponent(self):
        g = GoalEliminateOpponent(RED, BLUE)

        self.assertFalse(g.check(self.state), 'before attack, blue unit is still alive!')

        self.blue_tank.killed = True

        self.assertTrue(g.check(self.state), 'after attack, blue unit is still alive!')

    def testReachPoint(self):
        x1 = to_cube((4, 4))
        x2 = to_cube((5, 5))
        g = GoalReachPoint(RED, x1)

        self.gm.update(self.state)
        self.assertFalse(g.check(self.state), 'figure is still in starting position')

        m1 = Move(RED, self.red_tank, [x1])
        m2 = Move(RED, self.red_tank, [x2])

        self.gm.step(self.board, self.state, m1)
        self.assertFalse(g.check(self.state), 'figure moved to goal in this turn')

        self.gm.step(self.board, self.state, m2)
        self.assertFalse(g.check(self.state), 'figure moved outside of goal')

        self.gm.step(self.board, self.state, m1)
        self.assertFalse(g.check(self.state), 'figure is in position but not not long enough')
        self.gm.update(self.state)
        self.assertTrue(g.check(self.state), 'figure is in position since previous turn')

    def testEndTurn(self):
        g = GoalMaxTurn(RED, 2)

        self.gm.update(self.state)
        self.assertFalse(g.check(self.state), 'we are still in turn 1!')

        self.gm.update(self.state)
        self.assertTrue(g.check(self.state), 'we are already in turn 2!')

        self.gm.update(self.state)
        self.assertTrue(g.check(self.state), 'we are in turn 3, game should be ended!')
