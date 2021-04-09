import unittest

from core.utils.coordinates import Hex


class TestLOS(unittest.TestCase):

    def testConversion(self):
        for i in range(100):
            for j in range(100):
                h0 = Hex(t=(i, j))
                h1 = Hex(i, j)
                c1 = h1.cube()
                c2 = h0.cube()
                h2 = c1.hex()

                self.assertEqual(h0, h1, f'conversion error: {h0} -> {h1}')
                self.assertEqual(h0, h1, f'conversion error: {c1} -> {c2}')
                self.assertEqual(h1, h2, f'conversion error: {h1} -> {c2} -> {h2}')

    def testLerps(self):
        start = Hex(4, 1).cube()
        end = Hex(4, 6).cube()

        line = start.line(end)

        for i in range(1, 7):
            r = Hex(4, i).cube()
            h = line[i - 1].round()

            self.assertEqual(r, h, f'i={i} h={h} right={r}')
