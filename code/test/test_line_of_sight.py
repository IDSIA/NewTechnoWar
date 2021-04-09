import unittest

import numpy as np

from core.const import RED, BLUE
from core.figures import Tank, Infantry
from core.game import GameBoard, GameState, Terrain, GameManager
from core.utils.coordinates import Hex

GM: GameManager = GameManager()


class TestLOS(unittest.TestCase):

    def setUp(self):
        self.shape = (8, 8)
        self.board = GameBoard(self.shape)
        self.state = GameState(self.shape)

        self.blue_tank = Tank((4, 6), BLUE)
        self.red_tank = Tank((4, 1), RED)
        self.red_inf = Infantry((1, 4), RED)

        self.state.addFigure(self.red_tank, self.red_inf, self.blue_tank)

        los_on_target = self.state.getLOS(self.blue_tank)

        self.los_tank = los_on_target[self.red_tank.index]
        self.los_inf = los_on_target[self.red_inf.index]

    def testNoBlockers(self):
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_tank), 'tank has no LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'infantry has no LOS on target')

    def testDirectBlock(self):
        blocker = np.zeros(self.shape, 'uint8')
        blocker[4, 4] = 1  # continuously adding 1 will cycle through the type of terrains

        # road
        self.board.addTerrain(blocker)

        self.assertTrue(GM.checkLine(self.board, self.state, self.los_tank), 'road: tank has no LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'road: infantry has no LOS on target')

        # isolated tree
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'tree: tank has LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'tree: infantry has no LOS on target')

        # forest
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'forest: tank has LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'forest: infantry has no LOS on target')

        # wooden building
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'urban: tank has LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'urban: infantry has no LOS on target')

        # concrete building
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'building: tank has LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'building: infantry has no LOS on target')

    def testForestBlock(self):
        blocker = np.zeros(self.shape, 'uint8')
        blocker[4, 4] = Terrain.FOREST
        blocker[3, 6] = Terrain.FOREST
        blocker[4, 6] = Terrain.FOREST
        blocker[5, 6] = Terrain.FOREST
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'forest: tank has LOS on target')
        self.assertFalse(GM.checkLine(self.board, self.state, self.los_inf), 'forest: infantry has LOS on target')

    def testForestMarginNoBlock(self):
        blocker = np.zeros(self.shape, 'uint8')
        blocker[4, 6] = Terrain.FOREST
        blocker[3, 7] = Terrain.FOREST
        blocker[4, 7] = Terrain.FOREST
        blocker[5, 7] = Terrain.FOREST
        self.board.addTerrain(blocker)

        self.assertTrue(GM.checkLine(self.board, self.state, self.los_tank), 'forest: tank has LOS on target')
        self.assertTrue(GM.checkLine(self.board, self.state, self.los_inf), 'forest: infantry has LOS on target')

    def testBuildingBlock(self):
        blocker = np.zeros(self.shape, 'uint8')
        blocker[4, 4] = Terrain.CONCRETE_BUILDING
        blocker[3, 6] = Terrain.CONCRETE_BUILDING
        blocker[4, 6] = Terrain.CONCRETE_BUILDING
        blocker[5, 6] = Terrain.CONCRETE_BUILDING
        self.board.addTerrain(blocker)

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_tank), 'urban: tank has LOS on target')
        self.assertFalse(GM.checkLine(self.board, self.state, self.los_inf), 'urban: infantry has LOS on target')

    def testArmoredUnitBlock(self):
        dst = Hex(3, 5).cube()
        m1 = GM.actionMove(self.board, self.state, self.red_tank, destination=dst)

        # we move the tank in a blocking position
        GM.step(self.board, self.state, m1)

        los_on_target = self.state.getLOS(self.blue_tank)
        self.los_inf = los_on_target[self.red_inf.index]

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_inf), 'armored: inf has LOS on target')

    def testIndirectFire(self):
        blocker = np.zeros(self.shape, 'uint8')
        blocker[2, 5] = Terrain.CONCRETE_BUILDING
        blocker[3, 5] = Terrain.CONCRETE_BUILDING
        self.board.addTerrain(blocker)

        # we replace the blue tank with an infantry so we can use the mortar for an indirect hit
        self.state.clearFigures(BLUE)
        blue_inf = Infantry((4, 6), BLUE)
        self.state.addFigure(blue_inf)

        los_on_target = self.state.getLOS(blue_inf)
        self.los_inf = los_on_target[self.red_inf.index]

        self.assertFalse(GM.checkLine(self.board, self.state, self.los_inf), 'indirect: infantry has LOS on target')

        # self.blue_tank.kind = FigureType.INFANTRY

        self.assertTrue(
            GM.canShoot(self.board, self.state, self.red_inf, blue_inf, self.red_inf.weapons['MT']),
            'indirect: infantry cannot shot at the target'
        )
