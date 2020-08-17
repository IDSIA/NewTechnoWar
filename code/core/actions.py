from core.figures import Figure
from core.figures.weapons import Weapon

ACTION_PASS = 0
ACTION_ATTACK = 1
ACTION_MOVE = 2
ACTION_RESPONSE = 3


class Action:
    """Basic action class"""

    def __init__(self, agent: str, figure: Figure):
        """
        :param agent:   name of the agent
        :param figure:  Figure that performs the action
        """
        self.agent = agent
        self.figure = figure

    def __repr__(self):
        return f'{self.agent:5}: {self.figure.name:10}'


class Pass(Action):
    """Action that just does nothing: used to mark a Figure as activated."""

    def __init__(self, agent: str, figure: Figure):
        """
        :param agent:   name of the agent
        :param figure:  Figure that performs the action
        """
        super().__init__(agent, figure)

    def __repr__(self):
        return f'{super().__repr__()}: Pass'


class Move(Action):
    """Action to move a Figure to the destination."""

    def __init__(self, agent: str, figure: Figure, destination: list):
        """
        :param agent:           name of the agent
        :param figure:          Figure that performs the action
        :param destination:     path from current position to destination
        """
        super().__init__(agent, figure)
        self.destination = destination

    def __repr__(self):
        return f'{super().__repr__()}: Move to {self.destination[-1]}'


class LoadInto(Move):
    """Action to load a Figure in a transporter at the destination."""

    def __init__(self, agent: str, figure: Figure, destination: list, transporter: Figure):
        """
        :param agent:           name of the agent
        :param figure:          Figure that performs the action
        :param destination:     path from current position to destination
        :param transporter:     Figure to use as a transporter
        """
        super().__init__(agent, figure, destination)
        self.transporter = transporter

    def __repr__(self):
        return f'{super().__repr__()} load into {self.transporter}'


class Attack(Action):
    """Action to attack at another Figure."""

    def __init__(self, agent: str, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param agent:   name of the agent
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(agent, figure)
        self.target = target
        self.guard = guard
        self.weapon = weapon
        self.los = los
        self.lof = lof

    def __repr__(self):
        return f'{super().__repr__()}: Attack {self.target} with {self.weapon}'


class Respond(Attack):
    """Similar to Attack, but created only after a Attack Action."""

    def __init__(self, agent: str, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param agent:   name of the agent
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(agent, figure, target, guard, weapon, los, lof)

    def __repr__(self):
        return f'{super().__repr__()} in response'


class AttackGround(Action):
    """Similar to Attack, but aim to ground."""

    def __init__(self, agent: str, figure: Figure, ground: tuple, weapon: Weapon):
        """
        :param agent:   name of the agent
        :param figure:  Figure that performs the action
        :param ground:  Figure target of the action
        :param weapon:  weapon used by the attacker
        """
        super().__init__(agent, figure)
        self.ground = ground
        self.weapon = weapon

    def __repr__(self):
        return f'{super().__repr__()}: Attack ground at {self.ground} with {self.weapon}'
