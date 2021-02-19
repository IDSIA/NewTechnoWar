import unittest

from core.utils.coordinates import Hex, hex_to_cube, cube_to_hex, to_hex, to_cube, cube_linedraw, cube_round


class TestLOS(unittest.TestCase):

    def testConversion(self):
        for i in range(100):
            for j in range(100):
                h0 = to_hex((i, j))
                h1 = Hex(i, j)
                c1 = hex_to_cube(h1)
                c2 = to_cube((i, j))
                h2 = cube_to_hex(c1)

                self.assertEqual(h0, h1, f'conversion error: {h0} -> {h1}')
                self.assertEqual(h0, h1, f'conversion error: {c1} -> {c2}')
                self.assertEqual(h1, h2, f'conversion error: {h1} -> {c2} -> {h2}')

    def testLerps(self):
        start = to_cube((4, 1))
        end = to_cube((4, 6))

        line = cube_linedraw(start, end)

        for i in range(1, 7):
            r = to_cube((4, i))
            h = cube_round(line[i - 1])

            self.assertEqual(r, h, f'i={i} h={h} right={r}')
