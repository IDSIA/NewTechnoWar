from core.figures import Figure
from core.figures.weapons import Weapon

ACTION_ATTACK = 0
ACTION_MOVE = 1
ACTION_RESPONSE = 2


class Action:
    """Basic action class"""

    def __init__(self, agent: str, figure: Figure):
        self.agent = agent
        self.figure = figure

    def __repr__(self):
        return f'{self.agent:5} {self.figure.name:10}'


class DoNothing(Action):
    """Action that just does nothing: used to mark a Figure as activated."""

    def __init__(self, agent: str, figure: Figure):
        super().__init__(agent, figure)

    def __repr__(self):
        return f'{super().__repr__()}: Pass'


class Move(Action):
    """Action to move a Figure to the destination."""

    def __init__(self, agent: str, figure: Figure, destination: list):
        super().__init__(agent, figure)
        self.destination = destination

    def __repr__(self):
        return f'{super().__repr__()}: Move to {self.destination[-1]}'


class Shoot(Action):
    """Action to shoot at another Figure."""

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon, los: list):
        super().__init__(agent, figure)
        self.target = target
        self.weapon = weapon
        self.los = los

    def __repr__(self):
        return f'{super().__repr__()}: Shoot at {self.target} with {self.weapon}'


class Respond(Shoot):
    """Similar to Shoot, but created only after a Shoot Action."""

    def __init__(self, agent: str, figure: Figure, target: Figure, weapon: Weapon, los: list):
        super().__init__(agent, figure, target, weapon, los)

    def __repr__(self):
        return f'{super().__repr__()} in response'
