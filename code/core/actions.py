from core import Terrain
from core.figures import Figure
from core.weapons import Weapon
from utils.coordinates import Cube


class Action:
    """Basic action class"""

    def __init__(self, agent: str, figure: Figure):
        self.agent = agent
        self.figure = figure


class DoNothing(Action):
    """Action that just does nothing: used to mark a Figure as activated."""

    def __init__(self, agent: str, figure: Figure):
        super().__init__(agent, figure)

    def __repr__(self):
        return f'{self.agent}\t{self.figure.name}\tPass'


class Move(Action):
    """Action to move a Figure to the destination."""

    def __init__(self, agent: str, figure: Figure, destination: Cube):
        super().__init__(agent, figure)
        self.destination = destination

    def __repr__(self):
        return f'{self.agent}\t{self.figure.name}\tMove to {self.destination}'


class Shoot(Action):
    """Action to shoot at another Figure."""

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon, terrain: Terrain, los: list):
        super().__init__(agent, figure)
        self.target = target
        self.weapon = weapon
        self.terrain = terrain
        self.los = los

    def __repr__(self):
        return f'{self.agent}\t{self.figure.name}\tShoot at {self.target} with {self.weapon}'


class Respond(Shoot):
    """Similar to Shoot, but created only after a Shoot Action."""

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon, terrain: Terrain, los: list):
        super().__init__(agent, figure, target, weapon, terrain, los)

    def __repr__(self):
        return f'{self.agent}\t{self.figure.name}\tRespond to {self.target} with {self.weapon}'
