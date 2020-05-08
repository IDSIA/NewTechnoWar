from core import Terrain
from core.figures import Figure
from core.weapons import Weapon
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
        return f'{self.agent}\t{self.figure.name}\tMove to {self.destination}'


class Shoot(Action):

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon, terrain: Terrain):
        super().__init__(agent, figure)
        self.target = target
        self.weapon = weapon
        self.terrain = terrain

    def __repr__(self):
        return f'{self.agent}\t{self.figure.name}\tShoot {self.target} with {self.weapon}'


class Respond(Action):

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon):
        super().__init__(agent, figure)
        self.target = target
        self.weapon = weapon
