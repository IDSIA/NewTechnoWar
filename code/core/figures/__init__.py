"""
This module defines the available figures and their rules.
"""
import uuid

from core.figures.status import FigureStatus
from core.figures.types import FigureType
from core.figures.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle, \
    INFINITE
from core.game import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, ENDURANCE_EXO
from utils.coordinates import Cube, to_cube


# TODO: this should be a UNIT
class Figure:
    """Describe the actions and properties of a Unit."""

    # TODO: conversion to status array, position is a matrix of zeros

    def __init__(self, position: tuple, name: str, kind: int = FigureType.INFANTRY):
        self.fid = str(uuid.uuid4())

        self.name: str = name
        self.index: int = -1

        self.kind: int = kind

        self.move: int = 0
        self.load: int = 0
        self.hp: int = 0

        self.defense_basic: int = 1
        self.defense_smoke: int = 0

        self.weapons: list = []

        self.int_atk: int = 0
        self.int_def: int = 0
        self.endurance: int = 0

        self.stat: int = 0  # no effect

        if len(position) == 3:
            self.position: Cube = position
        else:
            self.position: Cube = to_cube(position)

        self.activated: bool = False
        self.responded: bool = False
        self.killed: bool = False
        self.hit: bool = False

        self.attackedBy = None

    def update(self, turn: int):
        self.endurance = ENDURANCE[turn]
        self.int_atk = INTELLIGENCE_ATTACK[turn]
        self.int_def = INTELLIGENCE_DEFENSE[turn]

    # hit score functions
    def setSTAT(self, new_STAT: FigureStatus):
        self.stat = new_STAT.value

    # actions related methods
    def goto(self, destination: Cube):
        self.position = destination

    def canRespond(self, attacker):
        self.attackedBy = attacker

    def __repr__(self):
        return f'{self.name}({self.position})'


class Tank(Figure):
    """3 red tanks"""

    def __init__(self, position: tuple, name: str = 'Tank'):
        super().__init__(position, name, FigureType.VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense_basic = 5
        self.defense_smoke = 18

        self.weapons = [
            MachineGun(INFINITE),
            Cannon(8),
            SmokeGrenade(2)
        ]


class APC(Figure):
    """1 blue armoured personnel carrier"""

    def __init__(self, position: tuple, name: str = 'APC'):
        super().__init__(position, name, FigureType.VEHICLE)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense_basic = 5
        self.defense_smoke = 18

        self.weapons = [
            MachineGun(INFINITE),
            SmokeGrenade(2)
        ]


class Infantry(Figure):
    """6x4 red and 2x4 blue"""

    def __init__(self, position: tuple, name: str = 'Infantry'):
        super().__init__(position, name)
        self.move = 4
        self.load = 1
        self.hp = 4

        self.weapons = [
            AssaultRifle(INFINITE),
            MachineGun(5),
            AntiTank(4),
            Mortar(2),
            Grenade(2)
        ]


class Exoskeleton(Infantry):
    """
        3 exoskeleton
        The exoskeleton is a device worn by soldiers to enhance their physical strength,
        endurance and ability to carry heavy loads.
    """

    def __init__(self, position: tuple, name: str = 'Exoskeleton'):
        super().__init__(position, name)
        self.move = 4
        self.load = 0
        self.hp = 4

        self.weapons = [
            AssaultRifle(INFINITE),
            MachineGun(2),
            AntiTank(4),
            Mortar(5),
            Grenade(2)
        ]

    def update(self, turn: int):
        super(Exoskeleton, self).update(turn)
        self.endurance = ENDURANCE_EXO[turn]


class Sniper(Infantry):
    """
        Special unit based on scenario
        The sniper has a status advantage of +2 and an accuracy advantage of +3 (+5 in total) added to his hit score
    """

    def __init__(self, position: tuple, name: str = 'Sniper'):
        super().__init__(position, name)
        self.move = 0
        self.hp = 4

        self.weapons = [
            SniperRifle(INFINITE)
        ]

    def setSTAT(self, STAT: FigureStatus):
        self.stat = STAT.value + 5


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: tuple, name: str = 'Civilian'):
        super().__init__(position, name, FigureType.OTHER)
        self.move = 0
        self.load = 0
        self.hp = 1
