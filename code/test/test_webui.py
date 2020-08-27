import unittest

from core import RED, BLUE
from web.server import create_app


class TestWebUI(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def testIndex(self):
        r = self.client.get('/', follow_redirects=True)

        self.assertEqual(r.status_code, 200)

    def initGame(self, redPlayer, bluePlayer, scenario, seed=1):
        r = self.client.post('/', follow_redirects=True, data={
            'seed': seed,
            'redPlayer': redPlayer,
            'bluePlayer': bluePlayer,
            'autoplay': False,
            'scenario': scenario,
            'replay': '',
        })

        self.assertEqual(r.status_code, 200)

    def action(self, data=None):
        if data:
            r = self.client.post('/game/human/click', data=data)
            self.assertEqual(r.status_code, 200)

        r = self.client.get('/game/next/step')
        self.assertEqual(r.status_code, 200)

        return r

    def testPlayRedHuman(self):
        self.initGame('Human', 'PlayerDummy', 'Dummy1', seed=1)

        # 1 ---------------------------------------------------------

        # T1: red action
        self.action(clickMove(RED, 1, 7, 4))
        # T1: blue response
        self.action()

        # T1: blue action
        self.action()
        # T1: red response
        self.action(clickPass(RED, 0))

        # T1: red action
        self.action(clickAttack(RED, 0, 'AR', BLUE, 0))
        # T1: blue response
        self.action()

        # 2 ---------------------------------------------------------

        # T2: red action
        self.action(clickMove(RED, 0, 5, 4))
        # T2: blue response
        self.action()

        # T2: blue action
        self.action()
        # T2: red response
        self.action(clickPass(RED, 0))

        # T2: red action
        self.action(clickMove(RED, 1, 5, 7))
        # T2: blue response
        self.action()

        # 3 ---------------------------------------------------------

        # T3: red action
        self.action(clickMove(RED, 0, 5, 5))
        # T3:blue response
        self.action()

        # T3: blue action
        self.action()
        # T3: red response
        self.action(clickAttack(RED, 0, 'AR', BLUE, 0))

        # T3: red action
        self.action(clickMove(RED, 1, 6, 4))
        # T3: blue response
        self.action()

        # 4 ---------------------------------------------------------

        # T4: red action
        self.action(clickAttack(RED, 0, 'GR', BLUE, 0))
        r = self.action()

        self.assertTrue(r.data['end'])


def clickMove(team, idx, x, y):
    return {
        'action': 'move',
        'team': team,
        'idx': str(idx),
        'x': str(x),
        'y': str(y),
    }


def clickAttack(team, idx, w, target_team, target_idx, x=-1, y=-1):
    return {
        'action': 'attack',
        'team': team,
        'idx': str(idx),
        'weapon': w,
        'targetTeam': target_team,
        'targetIdx': target_idx,
        'x': str(x),
        'y': str(y),
    }


def clickPass(team, idx, x=-1, y=-1):
    return {
        'action': 'pass',
        'team': team,
        'idx': str(idx),
        'x': str(x),
        'y': str(y),
    }


if __name__ == '__main__':
    unittest.main()
