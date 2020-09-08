"""
This module defines the available figures and their rules.
"""
import uuid
from typing import Dict, List

from core.figures.status import FigureStatus, NO_EFFECT, LOADED
from core.figures.types import FigureType
from core.figures.weapons import AntiTank, AssaultRifle, Cannon, Grenade, MachineGun, Mortar, SmokeGrenade, SniperRifle, \
    Weapon, WEAPON_KEY_LIST
from core.game import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE, ENDURANCE_EXO
from utils import INFINITE
from utils.coordinates import Cube, to_cube

DEFENSE_KEY_LIST = ['basic', 'smoke', 'antitank']


class Figure:
    """Describe the actions and properties of a Unit."""

    __slots__ = [
        'fid', 'team', 'name', 'index', 'kind', 'move', 'load', 'hp', 'hp_max', 'defense', 'weapons',
        'int_atk', 'int_def', 'endurance', 'stat', 'position', 'activated', 'responded', 'killed', 'hit',
        'attacked_by', 'can_transport', 'transport_capacity', 'transporting', 'transported_by', 'bonus'
    ]

    def __init__(self, position: tuple or Cube, name: str, team: str, kind: int, stat: FigureStatus):
        self.fid = str(uuid.uuid4())
        self.team: str = team

        self.name: str = name
        self.index: int = -1

        self.kind: int = kind

        self.move: int = 0
        self.load: int = 0
        self.hp: int = 0
        self.hp_max: int = 0

        self.defense: Dict[str, int] = {
            'basic': 1,
            'smoke': 18
        }
        self.weapons: Dict[str, Weapon] = {}

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

        self.attacked_by: int = -1

        self.can_transport: bool = False
        self.transport_capacity: int = 0
        self.transporting: List[int] = []
        self.transported_by: int = -1

    def vector(self) -> tuple:
        """Data on the figure in vectorized version, used for internal hashing."""
        data = [
            self.fid,
            self.team,
            self.name,
            self.index,
            self.kind,
            self.move,
            self.load,
            self.hp,
            self.hp_max,
            self.int_atk,
            self.int_def,
            self.endurance,
            self.stat,
            self.bonus,
            self.activated,
            self.responded,
            self.killed,
            self.hit,
            self.attacked_by,
            self.can_transport,
            self.transport_capacity,
            len(self.transporting),
            self.transported_by
        ]

        data += list(self.position)

        for d in DEFENSE_KEY_LIST:
            data.append(self.defense[d] if d in self.defense else 0)

        for w in WEAPON_KEY_LIST:
            data.append(self.weapons[w].ammo if w in self.weapons else 0)

        return tuple(data)

    def __eq__(self, other):
        if not isinstance(other, Figure):
            return False
        if not other:
            return False
        v = self.vector()
        v_other = other.vector()
        for i in range(len(v)):
            if v[i] != v_other[i]:
                return False
        return True

    def __hash__(self):
        return hash(self.vector())

    def update(self, turn: int) -> None:
        self.endurance = ENDURANCE[turn]
        self.int_atk = INTELLIGENCE_ATTACK[turn]
        self.int_def = INTELLIGENCE_DEFENSE[turn]

    def goto(self, destination: Cube) -> None:
        self.position = destination

    def transportLoad(self, figure) -> None:
        if not self.canTransport(figure):
            raise ValueError('cannot load figure')
        self.transporting.append(figure.index)
        figure.transported_by = self.index
        figure.stat = LOADED

    def transportUnload(self, figure) -> None:
        self.transporting.remove(figure.index)
        figure.transported_by = -1

    def canTransport(self, figure) -> bool:
        if figure.kind == FigureType.VEHICLE:
            return False
        return self.can_transport and len(self.transporting) < self.transport_capacity

    def getKey(self) -> str:
        return f'{self.team}{self.index}'

    def addWeapon(self, w: Weapon) -> None:
        self.weapons[w.wid] = w

    def __repr__(self) -> str:
        return f'{self.name}{self.position}'


class Tank(Figure):
    """3 red tanks"""

    def __init__(self, position: tuple, team: str, name: str = 'Tank', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, team, FigureType.VEHICLE, stat)
        self.move = 7
        self.load = 1
        self.hp = 1
        self.hp_max = 1

        self.defense: dict = {
            'basic': 5,
            'smoke': 18,
            'antitank': 0
        }

        self.addWeapon(MachineGun(INFINITE))
        self.addWeapon(Cannon(8))
        self.addWeapon(SmokeGrenade(2))

        self.can_transport = True
        self.transport_capacity = 2


class APC(Figure):
    """1 blue armoured personnel carrier"""

    def __init__(self, position: tuple, team: str, name: str = 'APC', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, team, FigureType.VEHICLE, stat)
        self.move = 7
        self.load = 1
        self.hp = 1
        self.hp_max = 1

        self.defense: dict = {
            'basic': 5,
            'smoke': 18,
            'antitank': 0
        }

        self.addWeapon(MachineGun(INFINITE))
        self.addWeapon(SmokeGrenade(2))

        self.can_transport = True
        self.transport_capacity = 2


class Infantry(Figure):
    """6x4 red and 2x4 blue"""

    def __init__(self, position: tuple, team: str, name: str = 'Infantry', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, team, FigureType.INFANTRY, stat)
        self.move = 4
        self.load = 1
        self.hp = 4
        self.hp_max = 4

        self.addWeapon(AssaultRifle(INFINITE))
        self.addWeapon(MachineGun(5))
        self.addWeapon(AntiTank(4))
        self.addWeapon(Mortar(2))
        self.addWeapon(Grenade(2))


class Exoskeleton(Infantry):
    """
        3 exoskeleton
        The exoskeleton is a device worn by soldiers to enhance their physical strength,
        endurance and ability to carry heavy loads.
    """

    def __init__(self, position: tuple, team: str, name: str = 'Exoskeleton', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, team, name, stat)
        self.move = 4
        self.load = 0
        self.hp = 4
        self.hp_max = 4

        self.addWeapon(AssaultRifle(INFINITE))
        self.addWeapon(MachineGun(2))
        self.addWeapon(AntiTank(4))
        self.addWeapon(Mortar(5))
        self.addWeapon(Grenade(2))

    def update(self, turn: int):
        super(Exoskeleton, self).update(turn)
        self.endurance = ENDURANCE_EXO[turn]


class Sniper(Infantry):
    """
        Special unit based on scenario
        The sniper has a status advantage of +2 and an accuracy advantage of +3 (+5 in total) added to his hit score
    """

    def __init__(self, position: tuple, team: str, name: str = 'Sniper', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, team, name, stat)
        self.move = 0
        self.hp = 4
        self.hp_max = 4

        self.addWeapon(SniperRifle(INFINITE))

        self.bonus = 5


class Civilian(Figure):
    """4 civilians"""

    def __init__(self, position: tuple, team: str, name: str = 'Civilian', stat: FigureStatus = NO_EFFECT):
        super().__init__(position, name, team, FigureType.OTHER, stat)
        self.move = 0
        self.load = 0
        self.hp = 1
        self.hp_max = 1
