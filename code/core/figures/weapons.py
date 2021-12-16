"""
This module contains a description of all weapons and their rules.
"""
from core.const import INFINITE

import numpy as np


def vectorWeaponInfo(meta: str) -> tuple:
    return (
        meta + "_max_range",
        meta + "_atk_normal",
        meta + "_atk_response",
        meta + "_ammo",
        meta + "_ammo_max",
        meta + "_dices",
        meta + "_curved",
        meta + "_damage",
        meta + "_antitank",
        meta + "_miss_matrix",
        meta + "_disabled",
        meta + "_attack_ground",
        meta + "_smoke",
    )


class Weapon:
    """
    Generic class for weapons mechanics.
    """
    __slots__ = [
        'tag', 'idx', 'name', 'max_range', 'atk_normal', 'atk_response', 'ammo', 'ammo_max', 'dices', 'curved', 'damage',
        'antitank', 'miss_matrix', 'disabled', 'attack_ground', 'smoke',
    ]

    def __init__(self, tag: str = '', idx: int = -1, name: str = '', max_range: int = 0, atk_normal: int = 0, atk_response: int = 0,
                 ammo: int = 0, dices: int = 1, curved: bool = False, damage: int = 1, antitank: bool = False,
                 miss_matrix: bool = False, attack_ground: bool = False, smoke: bool = False):
        self.tag: str = tag
        self.idx: int = idx
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

    def vector(self) -> np.ndarray:
        if self.ammo == 0 or self.disabled:
            return np.zeros(13, np.float64)

        return np.array([
            self.max_range,
            self.atk_normal,
            self.atk_response,
            self.ammo,
            self.ammo_max,
            self.dices,
            self.curved,
            self.damage,
            self.antitank,
            self.miss_matrix,
            self.disabled,
            self.attack_ground,
            self.smoke
        ], np.float64)


class Cannon(Weapon):
    """Tank weapon"""

    def __init__(self, ammo=8, dices_to_roll=1):
        super().__init__('CA', 0, 'Cannon', 75, 8, 4, ammo, dices_to_roll, antitank=True)


class AssaultRifle(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=INFINITE, dices_to_roll=4):
        super().__init__('AR', 1, 'Assault Rifle', 10, 6, 3, ammo, dices_to_roll)


class MachineGun(Weapon):
    """Tank and infantry weapon"""

    def __init__(self, ammo=5, dices_to_roll=1):
        super().__init__('MG', 2, 'Machine gun', 24, 8, 4, ammo, dices_to_roll, damage=4)


class AntiTank(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=4, dices_to_roll=1):
        super().__init__('AT', 3, 'Anti-tank weapon', 18, 10, 5, ammo, dices_to_roll, antitank=True)


class Mortar(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('MT', 4, 'Mortar', INFINITE, 12, 6, ammo, dices_to_roll, curved=True, damage=4, miss_matrix=True,
                         attack_ground=True)


class Grenade(Weapon):
    """Infantry weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('GR', 5, 'Grenade', 3, 18, 9, ammo, dices_to_roll, curved=True, damage=4)


class SmokeGrenade(Weapon):
    """Tank weapon"""

    def __init__(self, ammo=2, dices_to_roll=1):
        super().__init__('SM', 6, 'Smoke Grenade', 3, 20, 10, ammo, dices_to_roll, curved=True, damage=0,
                         attack_ground=True, smoke=True)


class SniperRifle(Weapon):
    """Infantry weapon, special case of Assault Rifle"""

    # TODO: ignore obstacles up to 3 tiles

    def __init__(self, ammo=INFINITE, dices_to_roll=1):
        super().__init__('SR', 7, 'Sniper Rifle', 10, 6, 3, ammo, dices_to_roll)
