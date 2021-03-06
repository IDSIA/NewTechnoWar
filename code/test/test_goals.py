import unittest

from os.path import join, dirname

from core.actions import Move
from core.const import RED, BLUE
from core.game import GameBoard, GameState, GoalMaxTurn, GoalReachPoint, GoalEliminateOpponent, GameManager
from core.templates import buildFigure
from core.utils.coordinates import Hex
from utils.setup_logging import setup_logging

setup_logging(join(dirname(__file__), 'logger.config.yaml'))

GM: GameManager = GameManager()


class TestGoals(unittest.TestCase):

    def setUp(self):
        shape = (8, 8)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.blue_tank = buildFigure('Tank', (6, 4), BLUE)
        self.red_tank = buildFigure('Tank', (1, 4), RED)
        self.red_inf = buildFigure('Infantry', (2, 4), RED)

        self.state.addFigure(self.red_tank, self.red_inf, self.blue_tank)

    def testEliminateOpponent(self):
        g = GoalEliminateOpponent(RED, BLUE)

        self.assertFalse(g.check(self.state), 'before attack, blue unit is still alive!')

        self.blue_tank.killed = True

        self.assertTrue(g.check(self.state), 'after attack, blue unit is still alive!')

    def testReachPoint(self):
        x1 = Hex(4, 4).cube()
        x2 = Hex(5, 5).cube()
        g = GoalReachPoint(RED, self.board.shape, [x1.hex()])

        GM.update(self.state)
        self.assertFalse(g.check(self.state), 'figure is still in starting position')

        m1 = Move(self.red_tank, [x1])
        m2 = Move(self.red_tank, [x2])

        GM.step(self.board, self.state, m1)
        self.assertFalse(g.check(self.state), 'figure moved to goal in this turn')

        GM.step(self.board, self.state, m2)
        self.assertFalse(g.check(self.state), 'figure moved outside of goal')

        GM.step(self.board, self.state, m1)
        self.assertFalse(g.check(self.state), 'figure is in position but not not long enough')
        GM.update(self.state)
        self.assertTrue(g.check(self.state), 'figure is in position since previous turn')

    def testEndTurn(self):
        g = GoalMaxTurn(RED, 2)

        GM.update(self.state)
        self.assertFalse(g.check(self.state), 'we are still in turn 1!')

        GM.update(self.state)
        self.assertTrue(g.check(self.state), 'we are already in turn 2!')

        GM.update(self.state)
        self.assertTrue(g.check(self.state), 'we are in turn 3, game should be ended!')
