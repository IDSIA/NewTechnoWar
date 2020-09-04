"""
This module contains a description of all weapons and their rules.
"""
from utils import INFINITE

WEAPON_KEY_LIST = ['CA', 'AR', 'MG', 'AT', 'MT', 'GR', 'SM', 'SR']


class Weapon:
    """
    Generic class for weapons mechanics.
    """
    __slots__ = [
        'wid', 'name', 'max_range', 'atk_normal', 'atk_response', 'ammo', 'ammo_max', 'dices', 'curved', 'damage',
        'antitank', 'miss_matrix', 'disabled', 'attack_ground', 'smoke',
    ]

    def __init__(self, _id: str, name: str, max_range: int, atk_normal: int, atk_response: int, ammo: int, dices: int,
                 curved: bool = False, damage: int = 1, antitank: bool = False, miss_matrix: bool = False,
                 attack_ground: bool = False, smoke: bool = False):
        self.wid: str = _id
        self.name: str = name
        self.max_range: int = max_range
        self.atk_normal: int = atk_normal
        self.atk_response: int = atk_response
        self.ammo: int = ammo
        self.ammo_max: int = ammo
        self.dices: int = dices
        self.curved: bool = curved
        self.damage: int = damage
        self.antitank: bool = antitank
        self.miss_matrix: bool = miss_matrix
        self.disabled: bool = False
        self.attack_ground: bool = attack_ground
        self.smoke: bool = smoke

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
        self.ammo = 0


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
        super().__init__('MG', 'Machine gun', 24, 8, 4, ammo, dices_to_roll, damage=4)


class AntiTank(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=4, dices_to_roll=1):
        super().__init__('AT', 'Anti-tank weapon', 18, 10, 5, ammo, dices_to_roll, antitank=True)


class Mortar(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('MT', 'Mortar', INFINITE, 12, 6, ammo, dices_to_roll, curved=True, damage=4, miss_matrix=True,
                         attack_ground=True)


class Grenade(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('GR', 'Grenade', 3, 18, 9, ammo, dices_to_roll, curved=True, damage=4)


class SmokeGrenade(Weapon):
    """Tank weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('SM', 'Smoke Grenade', 3, 20, 10, ammo, dices_to_roll, curved=True, damage=0,
                         attack_ground=True, smoke=True)


class SniperRifle(Weapon):
    """Infantry weapon, special case of Assault Rifle"""

    # TODO: ignore obstacles up to 3 tiles

    def __init__(self, ammo=INFINITE, dices_to_roll=1):
        super().__init__('SR', 'Sniper Rifle', 10, 6, 3, ammo, dices_to_roll)
