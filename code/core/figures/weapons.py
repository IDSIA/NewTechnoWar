"""
This module contains a description of all weapons and their rules.
"""
from utils import INFINITE


class Weapon:
    """
    Generic class for weapons mechanics.
    """
    __slots__ = [
        'wid', 'name', 'max_range', 'atk_normal', 'atk_response', 'ammo', 'dices', 'curved', 'damage', 'antitank',
        'disabled',
    ]

    def __init__(self, _id: str, name: str, max_range: int, atk_normal: int, atk_response: int, ammo: int, dices: int,
                 curved: bool = False, damage: int = 1, antitank: bool = False):
        self.wid: str = _id
        self.name: str = name
        self.max_range: int = max_range
        self.atk_normal: int = atk_normal
        self.atk_response: int = atk_response
        self.ammo: int = ammo
        self.dices: int = dices
        self.curved: bool = curved
        self.damage: int = damage
        self.antitank: bool = antitank
        self.disabled: bool = False

    def __repr__(self):
        return self.name

    def hasAmmo(self):
        return self.ammo > 0

    def isAvailable(self):
        return not self.disabled

    def shoot(self):
        self.ammo -= 1

    def disable(self):
        self.disabled = True


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
