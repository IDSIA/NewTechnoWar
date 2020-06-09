"""
This module defines the available figuresadn their rules.
"""
import uuid

from core import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, TOTAL_TURNS, FigureType
from core.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle, \
    INFINITE
from utils.coordinates import Cube, to_cube


def missMatrixRed(v: int) -> Cube:
    # range 2
    if v in [1, 3, 6, 12, 20]:
        return Cube(+2, -2, +0)
    if v in [2, 7, 13]:
        return Cube(+2, +0, -2)
    if v in [4, 5, 11]:
        return Cube(+0, -2, +2)
    if v == 8:
        return Cube(+0, +2, -2)
    if v == 9:
        return Cube(-2, +2, +0)
    if v == 10:
        return Cube(-2, +0, +2)
    # range 1
    if v == 14:
        return Cube(+0, +1, -1)
    if v == 15:
        return Cube(-1, +1, +0)
    if v == 16:
        return Cube(-1, +0, +1)
    if v == 17:
        return Cube(+0, -1, +1)
    if v == 18:
        return Cube(+1, -1, +0)
    if v == 19:
        return Cube(+1, +0, -1)

    # center
    return Cube(+0, +0, +0)


def missMatrixBlue(v: int) -> Cube:
    # range 2
    if v in [1, 3, 6, 12, 20]:
        return Cube(-2, +2, +0)
    if v in [2, 7, 13]:
        return Cube(+0, +2, -2)
    if v in [4, 5, 11]:
        return Cube(-2, +0, +2)
    if v == 8:
        return Cube(+2, +0, -2)
    if v == 9:
        return Cube(+2, -2, +0)
    if v == 10:
        return Cube(+0, -2, +2)
    # range 1
    if v == 14:
        return Cube(+0, -1, +1)
    if v == 15:
        return Cube(+1, -1, +0)
    if v == 16:
        return Cube(+1, +0, -1)
    if v == 17:
        return Cube(+0, +1, -1)
    if v == 18:
        return Cube(-1, +1, +0)
    if v == 19:
        return Cube(-1, +0, +1)

    # center
    return Cube(+0, +0, +0)


class FigureStatus:
    """Current status of a figure"""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


class StatusType:
    NO_EFFECT = FigureStatus('No effect', 0)
    IN_MOTION = FigureStatus('In motion', 3)  # the unit has already used its ability to move this turn
    UPSTAIRS = FigureStatus('Upstairs', 3)  # if the troops are on an upper flor of a house (scenario specified)
    UNDER_FIRE = FigureStatus('Under fire', -1)  # if the troops have already been targeted by a shot this turn
    CUT_OFF = FigureStatus('Cut off', 3)  # no friendly troop within 4 hexagons


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
        self.responded: bool = False
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

        self.defense = {'basic': 5, 'smoke': 18}
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

        self.defense = {'basic': 5, 'smoke': 18},
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

        self.defense = {'basic': 1}
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

        self.defense = {'basic': 1}
        self.weapons = [
            AssaultRifle(INFINITE),
            MachineGun(2),
            AntiTank(4),
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
        super().__init__(position, name)
        self.move = 0
        self.hp = 4

        self.weapons = [
            SniperRifle(INFINITE)
        ]

    def get_STAT(self):
        # TODO: better management of this change
        stat = super().get_STAT()
        return FigureStatus(stat.name, stat.value + 5)


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: tuple, name: str = 'Civilian'):
        super().__init__(position, name, FigureType.OTHER)
        self.move = 0
        self.load = 0
        self.hp = 1
