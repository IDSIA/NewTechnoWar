from collections import namedtuple

class Weapon(object):

    def __init__(self, id: str, name: str, max_range: int, atk: int, atk_reac: int, ammo: int):
        self.id = id
        self.name = name
        self.range = max_range
        self.atk = atk
        self.atk_reac = atk_reac
        self.ammo = ammo

# -1 stands for infinite
w_CA = Weapon('CA', 'Cannon',           75,  8,  4,  8)
w_AR = Weapon('AR', 'Assault Rifle',    10,  6,  3, -1)
w_MG = Weapon('MG', 'Machine gun',      24,  8,  4,  5)  # TODO: infinite ammo if tank
w_AT = Weapon('AT', 'Anti-tank weapon', 18, 10,  5,  4)
w_MT = Weapon('MT', 'Mortar',           -1, 12,  6,  2)
w_GR = Weapon('GR', 'Grenade',           3, 18,  9,  2)
w_GR = Weapon('SM', 'Smoke Grenade',     3, 20, 10,  2)

# TODO: miss matrix

STATUS = {
    0: ('In motion', 3),  # the unit has already used its ability to move this turn
    1: ('Upstairs', 3),  # if the troops are on an upper flor of a house (scenario specified)
    2: ('Under fire', -1),  # if the troops have already been targeted by a shot this turn
    3: ('Cut off', 3)  # no friendly troop within 4 hexagons
}

class Figure(object):

    def init(self, position: tuple, name: str, move_limit: int, load_limit: int, equipment: dict):
        self.position = position
        self.name = name

        self.move = move_limit
        self.load = load_limit
