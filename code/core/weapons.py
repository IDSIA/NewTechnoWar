"""
This module contains a description of all weapons and their rules.
"""


class Weapon:
    """
    Generic class for weapons mechanics.
    """

    def __init__(self, _id: str, name: str, max_range: int, atk_normal: int, atk_response: int, max_ammo: int, dices: int, curved: bool = False, damage: int = 1):
        self._id = _id
        self.name = name
        self.max_range = max_range
        self.atk_normal = atk_normal
        self.atk_response = atk_response
        self.max_ammo = max_ammo
        self.dices = dices
        self.curved = curved
        self.damage = damage

    def __repr__(self):
        return self.name


class Cannon(Weapon):
    """Tank weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('CA', 'Cannon', 75, 8, 4, max_ammunition, dices_to_roll)


class AssaultRifle(Weapon):
    """Infantry weapon"""

    def __init__(self, max_ammunition, dices_to_roll=4):
        super().__init__('AR', 'Assault Rifle', 10, 6, 3, max_ammunition, dices_to_roll)


class MachineGun(Weapon):
    """Tank and infantry weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('MG', 'Machine gun', 24, 8, 4, max_ammunition, dices_to_roll)


class AntiTank(Weapon):
    """Infantry weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('AT', 'Anti-tank weapon', 18, 10, 5, max_ammunition, dices_to_roll)


class Mortar(Weapon):
    """Infantry weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('MT', 'Mortar', 2e9, 12, 6, max_ammunition, dices_to_roll, True, 4)


class Grenade(Weapon):
    """Infantry weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('GR', 'Grenade', 3, 18, 9, max_ammunition, dices_to_roll, True, 4)


class SmokeGrenade(Weapon):
    """Tank weapon"""

    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('SM', 'Smoke Grenade', 3, 20, 10, max_ammunition, dices_to_roll, True)


class SniperRifle(Weapon):
    """Infantry weapon, special case of Assault Rifle"""

    def __init__(self, max_ammunition, dices_to_roll=4):
        super().__init__('SR', 'Sniper Rifle', 10, 6, 3, max_ammunition, dices_to_roll)
