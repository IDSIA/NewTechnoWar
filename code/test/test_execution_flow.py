import unittest

from os.path import join, dirname

from agents import MatchManager
from agents.adversarial.alphabeta import Puppet
from core.const import RED, BLUE
from core.templates import buildFigure
from core.game import GameBoard, GameState, GameManager
from utils.setup_logging import setup_logging

setup_logging(join(dirname(__file__), 'logger.config.yaml'))

GM: GameManager = GameManager()


class TestExecutionFlow(unittest.TestCase):

    def setUp(self):
        shape = (16, 16)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.inf_1 = buildFigure('Infantry', (4, 0), RED)
        self.inf_2 = buildFigure('Infantry', (8, 0), BLUE)

        self.state.addFigure(
            self.inf_1,
            self.inf_2,
        )

        self.red = Puppet(RED)
        self.red.action = GM.actionMove(self.board, self.state, self.inf_1, destination=self.inf_1.position)
        self.red.response = GM.actionNoResponse(RED)

        self.blue = Puppet(BLUE)
        self.blue.action = GM.actionMove(self.board, self.state, self.inf_2, destination=self.inf_2.position)
        self.blue.response = GM.actionNoResponse(BLUE)

        self.mm = MatchManager('', self.red, self.blue)

    def testFlowFromInit(self):
        self.mm.loadState(self.board, self.state)
        step, nextPlayer, _ = self.mm.nextPlayer()
        print(step, nextPlayer)

        self.assertEqual(step, 'round')
        self.assertEqual(nextPlayer, RED)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()
        print(step, nextPlayer)

        self.assertEqual(step, 'response')
        self.assertEqual(nextPlayer, BLUE)

    def testFlowFromResponse(self):
        response = GM.actionRespond(self.board, self.state, self.inf_2, self.inf_1, self.inf_2.weapons['AR'])
        GM.step(self.board, self.state, response)

        self.mm.loadState(self.board, self.state)
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'round')
        self.assertEqual(nextPlayer, BLUE)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'response')
        self.assertEqual(nextPlayer, RED)

    def testFlowUpdate(self):
        self.mm.loadState(self.board, self.state)
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'round')
        self.assertEqual(nextPlayer, RED)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'response')
        self.assertEqual(nextPlayer, BLUE)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'round')
        self.assertEqual(nextPlayer, BLUE)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'response')
        self.assertEqual(nextPlayer, RED)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'update')

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'round')
        self.assertEqual(nextPlayer, RED)

        self.mm.step()
        step, nextPlayer, _ = self.mm.nextPlayer()

        self.assertEqual(step, 'response')
        self.assertEqual(nextPlayer, BLUE)
