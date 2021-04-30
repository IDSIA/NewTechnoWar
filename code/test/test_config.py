import unittest

from core.const import RED, BLUE
from core.game import TERRAIN_TYPE
from core.game.terrain import TYPE_TERRAIN
from core.scenarios import buildScenario
from core.templates import collect


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        collect()

    def testScenarioJunction(self):
        board, state = buildScenario('Junction')

        self.assertFalse(state.has_placement[RED], "red should not have placement")
        self.assertTrue(state.has_placement[BLUE], "blue should have placement")

        self.assertTrue(state.has_choice[RED], "red should have choices")
        self.assertFalse(state.has_choice[BLUE], "blue should not have choices")

        self.assertEqual(len(state.choices[RED]), 3, "reds does not have 3 color choices")
        self.assertEqual(len(state.choices[BLUE]), 0, "blues should not have color choices")

        self.assertEqual(len(state.choices[RED]['orange']), 3, "orange should have 3 units")
        self.assertEqual(len(state.choices[RED]['lightred']), 3, "lightred should have 3 units")
        self.assertEqual(len(state.choices[RED]['darkred']), 3, "darkred should have 3 units")

        state.choose(RED, 'orange')

        redsIdx = [x.index for x in state.figures[RED]]
        bluesIdx = [x.index for x in state.figures[BLUE]]

        self.assertEqual(len(redsIdx), len(set(redsIdx)), "reds have duplicated index!")
        self.assertEqual(len(bluesIdx), len(set(bluesIdx)), "reds have duplicated index!")

    def testScenarioReplace(self):
        filename = 'config/scenarios/ScenarioJunction.yaml'
        with open(filename, 'r') as f:
            originalContent = f.readlines()

        newContent = [line for line in originalContent if 'color' not in line]

        try:
            # update content
            with open(filename, 'w') as f:
                f.writelines(newContent)
            collect()

            board, state = buildScenario('Junction')

            self.assertTrue(board)
            self.assertTrue(state)

            self.assertEqual(TYPE_TERRAIN[board.terrain[0, 0]], TERRAIN_TYPE['FOREST'])
            self.assertEqual(TYPE_TERRAIN[board.terrain[30, 30]], TERRAIN_TYPE['ROAD'])
        finally:

            # restore original content
            with open(filename, 'w') as f:
                f.writelines(originalContent)
