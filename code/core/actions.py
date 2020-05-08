from core.figures import Figure
from utils.coordinates import Cube


class Action:

    def __init__(self, agent: str, figure: Figure):
        self.agent = agent
        self.figure = figure


class Move(Action):

    def __init__(self, agent: str, figure: Figure, destination: Cube):
        super().__init__(agent, figure)
        self.destination = destination

    def __repr__(self):
        return f'{self.agent}:{self.figure.name} -> Move to {self.destination}'


class Shoot(Action):

    def __init__(self, agent: str, figure: Figure, target: Figure):
        super().__init__(agent, figure)
        self.target = target


class Respond(Action):

    def __init__(self, agent: str, figure: Figure, target: Figure):
        super().__init__(agent, figure)
        self.target = target
