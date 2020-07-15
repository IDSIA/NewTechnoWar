"""
This module defines the available figures and their rules.
"""
import uuid

from core.figures.status import FigureStatus, NO_EFFECT
from core.figures.types import FigureType
from core.figures.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle
from core.game import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, ENDURANCE_EXO
from utils.coordinates import Cube, to_cube
from utils import INFINITE


# TODO: this should be a UNIT
class Figure:
    """Describe the actions and properties of a Unit."""

    __slots__ = [
        'fid', 'name', 'index', 'kind', 'move', 'load', 'hp', 'defense', 'weapons',
        'int_atk', 'int_def', 'endurance', 'stat', 'position', 'activated', 'responded', 'killed', 'hit',
        'attacked_by', 'can_transport', 'transporting', 'transported_by', 'bonus'
    ]

    def __init__(self, position: tuple, name: str, kind: int, stat: FigureStatus):
        self.fid = str(uuid.uuid4())

        self.name: str = name
        self.index: int = -1

        self.kind: int = kind

        self.move: int = 0
        self.load: int = 0
        self.hp: int = 0

        self.defense: dict = {
            'basic': 1,
            'smoke': 0
        }
        self.weapons: list = []

        self.int_atk: int = 0
        self.int_def: int = 0
        self.endurance: int = 0

        self.stat: FigureStatus = stat
        self.bonus = 0

        if len(position) == 3:
            self.position: Cube = position
        else:
            self.position: Cube = to_cube(position)

        self.activated: bool = False
        self.responded: bool = False
        self.killed: bool = False
        self.hit: bool = False

        self.attacked_by = None

        self.can_transport: bool = False
        self.transporting: list = []
        self.transported_by = None

    def update(self, turn: int):
        self.endurance = ENDURANCE[turn]
        self.int_atk = INTELLIGENCE_ATTACK[turn]
        self.int_def = INTELLIGENCE_DEFENSE[turn]

    def goto(self, destination: Cube):
        self.position = destination

    def transport_load(self, figure):
        self.transporting.append(figure)
        figure.transported_by = self

    def transport_unload(self, figure):
        self.transporting.remove(figure)
        figure.transported_by = None

    def __repr__(self):
        return f'{self.name}({self.position})'


class Tank(Figure):
    """3 red tanks"""

    def __init__(self, position: tuple, name: str = 'Tank', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, FigureType.VEHICLE, stat)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense: dict = {
            'basic': 5,
            'smoke': 18,
            'antitank': 0
        }

        self.weapons = [
            MachineGun(INFINITE),
            Cannon(8),
            SmokeGrenade(2)
        ]

        self.can_transport = True


class APC(Figure):
    """1 blue armoured personnel carrier"""

    def __init__(self, position: tuple, name: str = 'APC', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, FigureType.VEHICLE, stat)
        self.move = 7
        self.load = 1
        self.hp = 1

        self.defense: dict = {
            'basic': 5,
            'smoke': 18,
            'antitank': 0
        }

        self.weapons = [
            MachineGun(INFINITE),
            SmokeGrenade(2)
        ]

        self.can_transport = True


class Infantry(Figure):
    """6x4 red and 2x4 blue"""

    def __init__(self, position: tuple, name: str = 'Infantry', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, FigureType.INFANTRY, stat)
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

    def __init__(self, position: tuple, name: str = 'Exoskeleton', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, stat)
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

    def __init__(self, position: tuple, name: str = 'Sniper', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, stat)
        self.move = 0
        self.hp = 4

        self.weapons = [
            SniperRifle(INFINITE)
        ]

        self.bonus = 5


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: tuple, name: str = 'Civilian', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, FigureType.OTHER, stat)
        self.move = 0
        self.load = 0
        self.hp = 1
