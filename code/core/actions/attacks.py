from core.actions.basics import ActionFigure
from core.figures.figure import Figure
from core.figures.weapons import Weapon
from core.utils.coordinates import Cube


class Attack(ActionFigure):
    """Action to perform an attack."""

    __slots__ = [
        'guard_id', 'guard_name', 'weapon_id', 'weapon_name', 'los', 'lof'
    ]

    def __init__(self, figure: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param figure:  Figure that performs the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(figure)
        self.guard_id = guard.index
        self.guard_name = guard.name
        self.weapon_id = weapon.wid
        self.weapon_name = repr(weapon)
        self.los = los
        self.lof = lof

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()


class AttackFigure(Attack):
    """Action to attack at another Figure."""

    __slots__ = [
        'target_id', 'target_name', 'target_team', 'guard_id', 'guard_name', 'weapon_id', 'weapon_name', 'los', 'lof'
    ]

    def __init__(self, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(figure, guard, weapon, los, lof)
        self.target_id = target.index
        self.target_name = target.name
        self.target_team = target.team

    def __repr__(self):
        return f'{super().__repr__()}: Attacks figure {self.target_name} with {self.weapon_name}'

    def __str__(self):
        return f'{super().__str__()}: Attacks figure {self.target_name} with {self.weapon_name}'


class AttackGround(Attack):
    """Similar to Attack, but it aims to the ground."""

    __slots__ = ['ground', 'weapon_id', 'weapon_name']

    def __init__(self, figure: Figure, ground: Cube, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param figure:  Figure that performs the action
        :param ground:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(figure, guard, weapon, los, lof)
        self.ground = ground
        self.weapon_id = weapon.wid
        self.weapon_name = repr(weapon)

    def __repr__(self):
        return f'{super().__repr__()}: Attacks ground at {self.ground} with {self.weapon_name}'

    def __str__(self):
        return f'{super().__str__()}: Attacks ground at {self.ground.hex()} with {self.weapon_name}'
