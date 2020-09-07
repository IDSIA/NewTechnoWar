import unittest

from core.const import RED, BLUE
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

    def step(self):
        self.response_step = self.client.get('/game/next/step')
        self.assertEqual(self.response_step.status_code, 200, 'invalid step')

    def action(self, data=None):
        if data:
            self.response_click = self.client.post('/game/human/click', data=data)
            self.assertEqual(self.response_click.status_code, 200, 'invalid action')

        self.step()

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

        self.step()  # 2 ---------------------------------------------------------

        # T2: red action
        self.action(clickMove(RED, 0, 5, 4))
        # T2: blue response
        self.action()

        # T2: blue action
        self.action()
        # T2: red response
        self.action(clickPass(RED, 0))

        # T2: red action
        self.action(clickMove(RED, 1, 4, 4))
        # T2: blue response
        self.action()

        self.step()  # 3 ---------------------------------------------------------

        # T3: red action
        self.action(clickMove(RED, 0, 4, 5))
        # T3:blue response
        self.action()

        # T3: blue action
        self.action()
        # T3: red response
        self.action(clickPass(RED, 0))

        self.assertTrue(self.response_step.json['state']['figures'][RED][1]['killed'], 'tank has not been killed')

        self.step()  # 4 ---------------------------------------------------------

        # T3: red action
        self.action(clickMove(RED, 0, 5, 5))
        # T3:blue response
        self.action()

        # T4: blue action
        self.action()
        # T4: red response
        self.action(clickPass(RED, 0))

        self.step()  # 5 ---------------------------------------------------------

        # T5: red action
        self.action(clickMove(RED, 0, 8, 3))
        # T5: blue response
        self.action()

        # T5: blue action
        self.action()
        # T5: red response
        # no response: blue passes!

        self.step()  # 6 ---------------------------------------------------------

        # T6: red action
        self.action(clickAttack(RED, 0, 'MG', BLUE, 0))
        # T6: blue response
        self.action()

        # T6: blue action
        self.action()
        # T6: red response
        self.action(clickPass(RED, 0))

        self.step()  # 7 ---------------------------------------------------------

        # T7: red action
        self.action(clickAttack(RED, 0, 'GR', BLUE, 0))

        self.step()  # check end game --------------------------------------------

        self.assertTrue(self.response_step.json['end'])

    def testPlayBlueHuman(self):
        self.initGame('PlayerDummy', 'Human', 'Dummy1', seed=2)

        # 1 ---------------------------------------------------------

        # T1: red action
        self.action()
        # T1: blue response
        self.action(clickAttack(BLUE, 0, 'MG', RED, 0))

        # T1: blue action
        self.action(clickMove(BLUE, 0, 5, 5))
        # T1: red response
        self.action()

        # T1: red action
        self.action()
        # T1: blue response
        self.action(clickAttack(BLUE, 0, 'AT', RED, 1))

        self.step()  # 2 ---------------------------------------------------------

        # T2: red action
        self.action()
        # T2: blue response
        self.action(clickPass(BLUE))

        # T2: blue action
        self.action(clickAttack(BLUE, 0, 'AT', RED, 1))
        # T2: red response
        self.action()

        # T2: red action
        self.action()
        # T2: blue response
        self.action(clickPass(BLUE))

        self.step()  # 3 ---------------------------------------------------------

        # T3: red action
        self.action()
        # T3:blue response
        self.action(clickAttack(BLUE, 0, 'MT', RED, 0))

        self.step()  # check end game --------------------------------------------

        self.assertTrue(self.response_step.json['end'])


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


def clickPass(team, idx=-1):
    if idx < 0:
        return {
            'action': 'pass',
            'team': team,
        }
    return {
        'action': 'pass',
        'team': team,
        'idx': str(idx),
    }


if __name__ == '__main__':
    unittest.main()
