"""
This module defines the available figuresadn their rules.
"""
from core.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle
from core import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, TOTAL_TURNS

# TODO: miss matrix

TYPE_OTHER = 0
TYPE_VEHICLE = 1
TYPE_INFANTRY = 2


class FigureStatus:
    """Current status of a figure"""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


FIGURE_STATUS = {
    0: FigureStatus('In motion', 3),  # the unit has already used its ability to move this turn
    1: FigureStatus('Upstairs', 3),  # if the troops are on an upper flor of a house (scenario specified)
    2: FigureStatus('Under fire', -1),  # if the troops have already been targeted by a shot this turn
    3: FigureStatus('Cut off', 3)  # no friendly troop within 4 hexagons
}


class Figure:
    """Describe the actions and properties of a Unit."""

    def __init__(self, position: tuple, name: str, kind: int):
        self.name = name

        self.kind = kind

        self.move = 0
        self.load = 0
        self.hp = 0

        self.defense = {}
        self.equipment = []

        self.int_atk = INTELLIGENCE_ATTACK
        self.int_def = INTELLIGENCE_DEFENSE
        self.endurance = ENDURANCE

        self.stat = 0
        self.position = position
        self.activated = False
        self.responded = False

    def set_STAT(self, new_STAT: FigureStatus):
        self.stat = new_STAT

    def get_STAT(self) -> FigureStatus:
        return self.stat

    def get_END(self, turn):
        return self.endurance[turn]

    def get_INT_ATK(self, turn):
        return self.int_atk[turn]

    def get_INT_DEF(self, turn):
        return self.int_def[turn]


class Tank(Figure):
    """3 red tanks"""

    def __init__(self, position: tuple, name: str = 'Tank'):
        super().__init__(position, name, TYPE_VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense = {'basic': 5, 'armored': 18}
        self.equipment = {
            MachineGun(-1),
            Cannon(8),
            SmokeGrenade(2)
        }


class APC(Figure):
    """1 blue armoured personnel carrier"""

    def __init__(self, position: tuple, name: str = 'APC'):
        super().__init__(position, name, TYPE_VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense = {'basic': 5, 'armored': 18},
        self.equipment = {
            MachineGun(-1),
            SmokeGrenade(2)
        }


class Infantry(Figure):
    """6x4 red and 2x4 blue"""

    def __init__(self, position: tuple, name: str = 'Infantry'):
        super().__init__(position, name, TYPE_INFANTRY)
        self.move = 4
        self.load = 1
        self.hp = 4

        self.defense = {'basic': 1}
        self.equipment = [
            AssaultRifle(-1),
            MachineGun(5, 4),
            AntiTank(4),
            Mortar(2),
            Grenade(2)
        ]


class Exoskeleton(Infantry):
    """
        3 exoskeleton
        The exoskeleton is a device worn by soldiers to enhance their physical strength, endurance and ability to carry heavy loads.
    """

    def __init__(self, position: tuple, name: str = 'Exoskeleton'):
        super().__init__(position, name, TYPE_INFANTRY)
        self.move = 4
        self.load = 0
        self.hp = 4

        self.defense = {'basic': 1}
        self.equipment = [
            AssaultRifle(-1),
            MachineGun(2),
            AntiTank(3),
            Mortar(5),
            Grenade(2)
        ]

        self.endurance = [4] * TOTAL_TURNS


class Sniper(Infantry):
    """
        Special unit based on scenario
        The sniper has a status advantage of +2 and an accuracy advantage of +3 (+5 in total) added to his hit score
    """

    def __init__(self, position: tuple, name: str = 'Sniper'):
        super().__init__(position, name, TYPE_INFANTRY)
        self.move = 0
        self.hp = 4  # TODO: it is single?

        self.equipment = [
            SniperRifle(-1)
        ]

    def get_STAT(self):
        return super().get_STAT + 5


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: tuple, name: str = 'Civilian'):
        super().__init__(position, name, TYPE_OTHER)
        self.move = 0
        self.load = 0
        self.hp = 1
