"""
This module contains a description of all weapons and their rules.
"""

# This is just a large number that can be considered an infinite amount of something
from core.figures import Figure, FigureType

INFINITE = 2000000000


class Weapon:
    """
    Generic class for weapons mechanics.
    """

    def __init__(self, _id: str, name: str, max_range: int, atk_normal: int, atk_response: int, ammo: int, dices: int,
                 curved: bool = False, damage: int = 1, antitank: bool = False):
        self._id = _id
        self.name = name
        self.max_range = max_range
        self.atk_normal = atk_normal
        self.atk_response = atk_response
        self.ammo = ammo
        self.dices = dices
        self.curved = curved
        self.damage = damage
        self.antitank = antitank
        self.no_effect = False

    def __repr__(self):
        return self.name

    def hasAmmo(self):
        return self.ammo > 0

    def validTarget(self, target: Figure):
        # TODO: verify this rule: can I use anti-tank against non-vehicles?
        if self.antitank:
            # can shoot only against vehicles
            return target.kind == FigureType.VEHICLE
        # can shoot against infantry and others only
        return target.kind < FigureType.VEHICLE

    def isAvailable(self):
        return not self.no_effect

    def shoot(self):
        self.ammo -= 1

    def disable(self):
        self.no_effect = True

    def canShoot(self, target: Figure, n: int, nObstacles: int):
        canHit = self.curved or nObstacles == 0
        hasAmmo = self.hasAmmo()
        available = self.isAvailable()
        isInRange = self.max_range >= n
        validTarget = self.validTarget(target)

        return all([canHit, hasAmmo, available, isInRange, validTarget])


class Cannon(Weapon):
    """Tank weapon"""

    def __init__(self, ammo=8, dices_to_roll=1):
        super().__init__('CA', 'Cannon', 75, 8, 4, ammo, dices_to_roll, antitank=True)


class AssaultRifle(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=INFINITE, dices_to_roll=4):
        super().__init__('AR', 'Assault Rifle', 10, 6, 3, ammo, dices_to_roll)


class MachineGun(Weapon):
    """Tank and infantry weapon"""

    def __init__(self, ammo=5, dices_to_roll=1):
        super().__init__('MG', 'Machine gun', 24, 8, 4, ammo, dices_to_roll)


class AntiTank(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=4, dices_to_roll=1):
        super().__init__('AT', 'Anti-tank weapon', 18, 10, 5, ammo, dices_to_roll, antitank=True)


class Mortar(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('MT', 'Mortar', INFINITE, 12, 6, ammo, dices_to_roll, True, 4)


class Grenade(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('GR', 'Grenade', 3, 18, 9, ammo, dices_to_roll, True, 4)


class SmokeGrenade(Weapon):
    """Tank weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('SM', 'Smoke Grenade', 3, 20, 10, ammo, dices_to_roll, True)


class SniperRifle(Weapon):
    """Infantry weapon, special case of Assault Rifle"""

    def __init__(self, ammo=INFINITE, dices_to_roll=1):
        super().__init__('SR', 'Sniper Rifle', 10, 6, 3, ammo, dices_to_roll)
