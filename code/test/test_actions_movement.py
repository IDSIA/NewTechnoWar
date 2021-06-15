import unittest

import numpy as np

from os.path import join, dirname

from core.const import RED
from core.figures.stats import stat
from core.game import GameManager
from core.game.board import GameBoard
from core.game.state import GameState
from core.game.terrain import TERRAIN_TYPE
from core.templates import collect, buildFigure
from core.utils.coordinates import Cube, Hex
from utils.setup_logging import setup_logging

setup_logging(join(dirname(__file__), 'logger.config.yaml'))

GM: GameManager = GameManager()


class TestMovementAction(unittest.TestCase):

    def setUp(self):
        collect()

        shape = (16, 16)
        self.board = GameBoard(shape)
        self.state = GameState(shape)

        self.tank = buildFigure('Tank', (8, 8), RED)
        self.state.addFigure(self.tank)

    def testMoveToDestination(self):
        dst = Hex(4, 4).cube()
        move = GM.actionMove(self.board, self.state, self.tank, destination=dst)

        GM.step(self.board, self.state, move)

        self.assertEqual(self.state.getFiguresByPos(move.team, move.destination)[0], self.tank,
                         'figure in the wrong position')
        self.assertEqual(self.tank.stat, stat('IN_MOTION'), 'figure should be in motion')
        self.assertEqual(self.tank.position, dst, 'figure not at the correct destination')

    def testMoveOnRoad(self):
        shape = (1, 16)
        board = GameBoard(shape)

        t = buildFigure('Tank', (0, 0), RED)
        i = buildFigure('Infantry', (0, 15), RED)

        stateTank = GameState(shape)
        stateTank.addFigure(t)

        stateInf = GameState(shape)
        stateInf.addFigure(i)

        # movements without road
        nTankNoRoad = len(GM.buildMovements(board, stateTank, t))
        nInfNoRoad = len(GM.buildMovements(board, stateInf, i))

        # adding road
        road = np.zeros(shape, 'uint8')
        road[0, :] = TERRAIN_TYPE['ROAD'].level
        board.addTerrain(road)

        # test for vehicles
        nTankRoad = len(GM.buildMovements(board, stateTank, t))
        nInfRoad = len(GM.buildMovements(board, stateInf, i))

        # tank
        self.assertNotEqual(nTankRoad, nTankNoRoad, 'road has no influence for tank')
        self.assertEqual(nTankRoad, 8, 'invalid distance with road for tank')
        self.assertEqual(nTankNoRoad, 6, 'invalid distance without road for tank')
        self.assertEqual(nTankRoad - nTankNoRoad, 2, 'road does not increase by 2 the distance for tank')

        # infantry
        self.assertNotEqual(nInfRoad, nInfNoRoad, 'road has no influence on infantry')
        self.assertEqual(nInfRoad, 4, 'invalid distance with road for infantry')
        self.assertEqual(nInfNoRoad, 3, 'invalid distance without road  for infantry')
        self.assertEqual(nInfRoad - nInfNoRoad, 1, 'road does not increase by 1 the distance for infantry')

        # test for road change
        board.terrain[0, 0] = 0
        board.terrain[0, 15] = 0

        nTankRoad = len(GM.buildMovements(board, stateTank, t))
        nInfRoad = len(GM.buildMovements(board, stateInf, i))

        self.assertEqual(nTankRoad, 8, 'invalid distance for tank')
        self.assertEqual(nInfRoad, 4, 'invalid distance for infantry')

    def testActivateMoveToDestination(self):
        dst = Hex(4, 4).cube()
        move = GM.actionMove(self.board, self.state, self.tank, destination=dst)

        self.state1, _ = GM.activate(self.board, self.state, move)
        self.assertNotEqual(hash(self.state1), hash(self.state),
                            'self.state1 and self.state0 are the same, should be different!')
        self.assertNotEqual(self.state.getFigure(move).position, self.state1.getFigure(move).position,
                            'figure is in teh same location for both self.state0 and self.state1!')

        self.state2, _ = GM.activate(self.board, self.state, move)
        self.assertNotEqual(hash(self.state2), hash(self.state),
                            'self.state2 and self.state0 are the same, should be different!')
        self.assertEqual(self.state1.getFigure(move).position, self.state2.getFigure(move).position,
                         'self.state1 and self.state2 have different end location')

        self.state3, _ = GM.activate(self.board, self.state, move)
        self.assertNotEqual(hash(self.state3), hash(self.state),
                            'self.state3 and self.state0 are the same, should be different!')
        self.assertEqual(self.state1.getFigure(move).position, self.state3.getFigure(move).position,
                         'self.state1 and self.state3 have different end location')
        self.assertEqual(self.state2.getFigure(move).position, self.state3.getFigure(move).position,
                         'self.state2 and self.state3 have different end location')

    def testMoveWithTransport(self):
        inf1 = buildFigure('Infantry', (7, 7), RED, 'Inf1', stat('NO_EFFECT'))
        inf2 = buildFigure('Infantry', (7, 8), RED, 'Inf2', stat('NO_EFFECT'))
        inf3 = buildFigure('Infantry', (7, 9), RED, 'Inf3', stat('NO_EFFECT'))

        # add infantry units
        self.state.addFigure(inf1)
        self.state.addFigure(inf2)
        self.state.addFigure(inf3)

        # load 2 units
        load1 = GM.actionLoadInto(self.board, self.state, inf1, self.tank)
        load2 = GM.actionLoadInto(self.board, self.state, inf2, self.tank)
        load3 = GM.actionLoadInto(self.board, self.state, inf3, self.tank)

        GM.step(self.board, self.state, load1)
        GM.step(self.board, self.state, load2)

        # load a third unit: cannot do that!
        self.assertRaises(ValueError, GM.step, self.board, self.state, load3)

        self.assertEqual(inf1.position, self.tank.position)
        self.assertEqual(inf2.position, self.tank.position)
        self.assertNotEqual(inf3.position, self.tank.position)

        # move figure in same position of tank
        move = GM.actionMove(self.board, self.state, inf3, destination=self.tank.position)
        GM.step(self.board, self.state, move)

        figures = self.state.getFiguresByPos(RED, self.tank.position)
        self.assertEqual(len(figures), 4, 'not all figures are in the same position')
        self.assertEqual(inf1.transported_by, self.tank.index, 'Inf1 not in transporter')
        self.assertEqual(inf2.transported_by, self.tank.index, 'Inf2 not in transporter')
        self.assertEqual(inf3.transported_by, -1, 'Inf3 is in transporter')

        # move tank
        dst = Hex(8, 2).cube()
        move = GM.actionMove(self.board, self.state, self.tank, destination=dst)
        GM.step(self.board, self.state, move)

        # figures moves along with tank
        self.assertEqual(inf1.position, self.tank.position, 'Inf1 not moved with transporter')
        self.assertEqual(inf2.position, self.tank.position, 'Inf2 not moved with transporter')
        self.assertEqual(len(self.tank.transporting), 2, 'Transporter not transporting all units')

        self.assertGreater(inf1.transported_by, -1)

        # unload 1 figure
        dst = Hex(8, 4).cube()
        move = GM.actionMove(self.board, self.state, inf1, destination=dst)
        GM.step(self.board, self.state, move)

        self.assertEqual(len(self.tank.transporting), 1, 'transporter has less units than expected')
        self.assertNotEqual(inf1.position, self.tank.position, 'Inf1 has not been moved together with transporter')

    def testMoveInsideShape(self):
        # top left
        dst = Hex(0, 0).cube()
        self.state.moveFigure(self.tank, dst=dst)

        moves = GM.buildMovements(self.board, self.state, self.tank)

        for move in moves:
            d: Cube = move.destination
            x, y = d.tuple()
            self.assertGreaterEqual(x, 0, f'moves outside of map limits: ({x},{y})')
            self.assertGreaterEqual(y, 0, f'moves outside of map limits: ({x},{y})')

        # bottom right
        dst = Hex(15, 15).cube()
        self.state.moveFigure(self.tank, dst=dst)

        moves = GM.buildMovements(self.board, self.state, self.tank)

        for move in moves:
            d: Cube = move.destination
            x, y = d.tuple()
            self.assertLess(x, 16, f'moves outside of map limits: ({x},{y})')
            self.assertLess(y, 16, f'moves outside of map limits: ({x},{y})')

    def testMoveOutsideShape(self):
        # outside of map
        dst = Hex(-1, -1).cube()
        self.state.moveFigure(self.tank, dst=dst)

        moves = GM.buildMovements(self.board, self.state, self.tank)

        self.assertEqual(len(moves), 0, 'moves outside of the map!')


if __name__ == '__main__':
    unittest.main()
