import numpy as np


class PlayerDummy:

    def __init__(self, team: str):
        self.name = 'dummy'
        self.team = team

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseFigure(self, figures: list):
        return np.random.choice(figures)

    def chooseActionType(self, types: list):
        return np.random.choice(types)

    def chooseAction(self, actions: list):
        return np.random.choice(actions)

    def chooseResponse(self):
        return np.random.choice([True, False])
