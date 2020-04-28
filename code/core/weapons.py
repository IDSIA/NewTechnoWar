class Weapon(object):

    def __init__(self, id: str, name: str, max_range: int, attack_normal: int, attack_response: int, max_mamunition: int, dices_to_roll:int):
        self.id = id
        self.name = name
        self.range = max_range
        self.attack_normal = attack_normal
        self.attack_response = attack_response
        self.max_mamunition = max_mamunition
        self.dices = dices_to_roll


class Cannon(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('CA', 'Cannon', 75, 8, 4, max_ammunition, dices_to_roll)


class AssaultRifle(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=4):
        super().__init__('AR', 'Assault Rifle', 10, 6, 3, max_ammunition, dices_to_roll)


class MachineGun(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('MG', 'Machine gun', 24, 8, 4, max_ammunition, dices_to_roll)


class AntiTank(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('AT', 'Anti-tank weapon', 18, 10,  5, max_ammunition, dices_to_roll)


class Mortar(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('MT', 'Mortar', -1, 12, 6, max_ammunition, dices_to_roll)


class Grenade(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('GR', 'Grenade', 3, 18, 9, max_ammunition, dices_to_roll)


class SmokeGrenade(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=1):
        super().__init__('SM', 'Smoke Grenade', 3, 20, 10, max_ammunition, dices_to_roll)


class SniperRifle(Weapon):
    def __init__(self, max_ammunition, dices_to_roll=4):
        super().__init__('SR', 'Sniper Rifle', 10, 6, 3, max_ammunition, dices_to_roll)
