from core.figures import Figure
from core.figures.weapons import Weapon
from utils.coordinates import Cube, cube_to_hex


class Action:
    """Basic action class"""

    __slots__ = ['team', 'figure_id', 'figure_name']

    def __init__(self, team: str, figure: Figure):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        """
        self.team = team
        self.figure_id = figure.index
        self.figure_name = figure.name

    def __repr__(self):
        return f'{self.team:5}: {self.figure_name:10}'

    def __str__(self):
        return f'{self.team.upper():5}: {self.figure_name:10}'


class Pass(Action):
    """Action that just does nothing: used to mark a Figure as activated."""

    def __init__(self, team: str, figure: Figure):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        """
        super().__init__(team, figure)

    def __repr__(self):
        return f'{super().__repr__()}: Pass'

    def __str__(self):
        return f'{super().__str__()}: Pass'


class Move(Action):
    """Action to move a Figure to the destination."""

    __slots__ = ['position', 'path', 'destination']

    def __init__(self, team: str, figure: Figure, path: list):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        :param path:    path from current position to destination
        """
        super().__init__(team, figure)
        self.position = figure.position
        self.path = path
        self.destination = path[-1]

    def __repr__(self):
        return f'{super().__repr__()}: Move to {self.destination}'

    def __str__(self):
        return f'{super().__str__()}: Moved to {cube_to_hex(self.destination)}'


class LoadInto(Move):
    """Action to load a Figure in a transporter at the destination."""

    __slots__ = ['transporter_id', 'transporter_name']

    def __init__(self, team: str, figure: Figure, destination: list, transporter: Figure):
        """
        :param team:            name of the team
        :param figure:          Figure that performs the action
        :param destination:     path from current position to destination
        :param transporter:     Figure to use as a transporter
        """
        super().__init__(team, figure, destination)
        self.transporter_id = transporter.index
        self.transporter_name = transporter.name

    def __repr__(self):
        return f'{super().__repr__()} and load into {self.transporter_name}'

    def __str__(self):
        return f'{super().__str__()} and loaded into {self.transporter_name}'


class Attack(Action):
    """Action to attack at another Figure."""

    __slots__ = ['target_id', 'target_name', 'target_team', 'guard_id', 'weapon_id', 'weapon_name', 'los', 'lof']

    def __init__(self, team: str, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(team, figure)
        self.target_id = target.index
        self.target_name = target.name
        self.target_team = target.team
        self.guard_id = guard.index
        self.weapon_id = weapon.wid
        self.weapon_name = repr(weapon)
        self.los = los
        self.lof = lof

    def __repr__(self):
        return f'{super().__repr__()}: Attack {self.target_name} with {self.weapon_name}'

    def __str__(self):
        return f'{super().__str__()}: Attack {self.target_name} with {self.weapon_name}'


class Respond(Attack):
    """Similar to Attack, but created only after a Attack Action."""

    def __init__(self, team: str, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(team, figure, target, guard, weapon, los, lof)

    def __repr__(self):
        return f'{super().__repr__()} in response'

    def __str__(self):
        return f'{super().__str__()} in response'


class AttackGround(Action):
    """Similar to Attack, but aim to ground."""

    __slots__ = ['ground', 'weapon_id', 'weapon_name']

    def __init__(self, team: str, figure: Figure, ground: Cube, weapon: Weapon):
        """
        :param team:    name of the team
        :param figure:  Figure that performs the action
        :param ground:  Figure target of the action
        :param weapon:  weapon used by the attacker
        """
        super().__init__(team, figure)
        self.ground = ground
        self.weapon_id = weapon.wid
        self.weapon_name = weapon.name

    def __repr__(self):
        return f'{super().__repr__()}: Attack ground at {self.ground} with {self.weapon_name}'

    def __str__(self):
        return f'{super().__str__()}: Attack ground at {cube_to_hex(self.ground)} with {self.weapon_name}'
