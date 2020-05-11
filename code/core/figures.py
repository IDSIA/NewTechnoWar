"""
This module defines the available figuresadn their rules.
"""
from core.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle
from core import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, TOTAL_TURNS
from utils.coordinates import Cube, to_cube

# TODO: miss matrix


class FigureType:
    """Defines the possible states of a Figure"""
    OTHER = 0
    VEHICLE = 1
    INFANTRY = 2


class FigureStatus:
    """Current status of a figure"""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


class StatusType:
    NO_EFFECT = FigureStatus('No effect', 0)
    IN_MOTION = FigureStatus('In motion', 3),  # the unit has already used its ability to move this turn
    UPSTAIRS = FigureStatus('Upstairs', 3),  # if the troops are on an upper flor of a house (scenario specified)
    UNDER_FIRE = FigureStatus('Under fire', -1),  # if the troops have already been targeted by a shot this turn
    CUT_OFF = FigureStatus('Cut off', 3)  # no friendly troop within 4 hexagons


class Figure:
    """Describe the actions and properties of a Unit."""

    def __init__(self, position: Cube, name: str, kind: int = FigureType.INFANTRY):
        self.name: str = name
        self.index: int = -1

        self.kind: int = kind

        self.move: int = 0
        self.load: int = 0
        self.hp: int = 0

        self.defense: dict = {}
        self.weapons: list = []

        self.int_atk: list = INTELLIGENCE_ATTACK
        self.int_def: list = INTELLIGENCE_DEFENSE
        self.endurance: list = ENDURANCE

        self.stat: FigureStatus = StatusType.NO_EFFECT

        if len(position) == 3:
            self.position: Cube = position
        else:
            self.position: Cube = to_cube(position)

        self.activated: bool = False
        self.respondable: bool = False
        self.killed: bool = False

        self.attackedBy = None

    # hit score functions
    def set_STAT(self, new_STAT: FigureStatus):
        self.stat = new_STAT

    def get_STAT(self) -> FigureStatus:
        return self.stat

    def get_END(self, turn: int) -> int:
        return self.endurance[turn]

    def get_INT_ATK(self, turn: int) -> int:
        return self.int_atk[turn]

    def get_INT_DEF(self, turn: int) -> int:
        return self.int_def[turn]

    # actions related methods
    def goto(self, destination: Cube):
        self.position = destination

    def canRespond(self, attacker):
        self.respondable = True
        self.attackedBy = attacker

    def __repr__(self):
        return f'{self.name}({self.position})'


class Tank(Figure):
    """3 red tanks"""

    def __init__(self, position: Cube, name: str = 'Tank'):
        super().__init__(position, name, FigureType.VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense = {'basic': 5, 'armored': 18}
        self.equipment = [
            MachineGun(2e9),
            Cannon(8),
            SmokeGrenade(2)
        ]


class APC(Figure):
    """1 blue armoured personnel carrier"""

    def __init__(self, position: Cube, name: str = 'APC'):
        super().__init__(position, name, FigureType.VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense = {'basic': 5, 'armored': 18},
        self.equipment = [
            MachineGun(2e9),
            SmokeGrenade(2)
        ]


class Infantry(Figure):
    """6x4 red and 2x4 blue"""

    def __init__(self, position: Cube, name: str = 'Infantry'):
        super().__init__(position, name)
        self.move = 4
        self.load = 1
        self.hp = 4

        self.defense = {'basic': 1}
        self.equipment = [
            AssaultRifle(2e9),
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

    def __init__(self, position: Cube, name: str = 'Exoskeleton'):
        super().__init__(position, name)
        self.move = 4
        self.load = 0
        self.hp = 4

        self.defense = {'basic': 1}
        self.equipment = [
            AssaultRifle(2e9),
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

    def __init__(self, position: Cube, name: str = 'Sniper'):
        super().__init__(position, name)
        self.move = 0
        self.hp = 4  # TODO: it is single?

        self.equipment = [
            SniperRifle(2e9)
        ]

    def get_STAT(self):
        # TODO: better management of this change
        stat = super().get_STAT()
        return FigureStatus(stat.name, stat.value+5)


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: Cube, name: str = 'Civilian'):
        super().__init__(position, name, FigureType.OTHER)
        self.move = 0
        self.load = 0
        self.hp = 1
