"""
This module defines the available figures and their rules.
"""
import uuid
from typing import Dict, List

from core.figures.defenses import DEFENSE_KEY_LIST
from core.figures.lists import DEFENSE_KEY_LIST, WEAPON_KEY_LIST
from core.figures.static import ENDURANCE, INTELLIGENCE_ATTACK, INTELLIGENCE_DEFENSE
from core.figures.stats import FigureStatus, stat
from core.figures.status import FigureStatus, STATS_LIST
from core.figures.types import FigureType
from core.figures.weapons import Weapon
from core.utils.coordinates import Cube, Hex


def vectorFigureInfo(meta: str) -> tuple:
    info = [
        meta + "_index",
        meta + "_kind",
        meta + "_end",
        meta + "_int_atk",
        meta + "_int_def",
        meta + "_move",
        meta + "_load",
        meta + "_hp",
        meta + "_hp_max",
        meta + "_bonus",
        meta + "_activated",
        meta + "_responded",
        meta + "_attacked",
        meta + "_moved",
        meta + "_passed",
        meta + "_killed",
        meta + "_hit",
        meta + "_attacked_by",
        meta + "_can_transport",
        meta + "_transport_capacity",
        meta + "_len_transporting",
        meta + "_transported_by",
        meta + "_positionX",
        meta + "_positionY",
        meta + "_positionZ",
        meta + "_stat_value",
    ]

    for s in STATS_LIST:
        info.append(meta + "_stat_" + s.name.replace(' ', ''))

    for w in WEAPON_KEY_LIST:
        info.append(meta + "_weapon_" + w)

    for d in DEFENSE_KEY_LIST:
        info.append(meta + "_defense_" + d)

    return tuple(info)


class Figure:
    """Describe the actions and properties of a Unit."""

    __slots__ = [
        'fid', 'team', 'name', 'index', 'kind', 'move', 'load', 'hp', 'hp_max', 'defense', 'weapons',
        'int_atk', 'int_def', 'endurance', 'stat', 'position', 'activated', 'responded', 'killed', 'hit',
        'attacked_by', 'can_transport', 'transport_capacity', 'transporting', 'transported_by', 'bonus',
        'attacked', 'moved', 'passed', 'color', 'updates'
    ]

    def __init__(self, position: tuple or Hex or Cube, name: str, team: str, kind: str, status: FigureStatus = None):
        self.fid = str(uuid.uuid4())
        self.team: str = team
        self.color: str = ''

        self.name: str = name
        self.index: int = -1

        self.kind: str = kind

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

        self.stat: FigureStatus = status
        self.bonus = 0

        if isinstance(position, Cube):
            self.position: Cube = position
        elif isinstance(position, Hex):
            self.position: Cube = position.cube()
        elif len(position) == 2:
            self.position: Cube = Hex(t=position).cube()
        else:
            self.position: Cube = Cube(t=position)

        self.activated: bool = False
        self.responded: bool = False
        self.attacked: bool = False
        self.moved: bool = False
        self.passed: bool = False
        self.killed: bool = False
        self.hit: bool = False

        self.attacked_by: int = -1

        self.can_transport: bool = False
        self.transport_capacity: int = 0
        self.transporting: List[int] = []
        self.transported_by: int = -1

        self.updates: list = []

    def vector(self) -> tuple:
        """Data on the figure in vectorized version, used for internal hashing."""
        data = [
            self.index,
            self.kind,
            self.endurance,
            self.int_atk,
            self.int_def,
            self.move,
            self.load,
            self.hp,
            self.hp_max,
            self.bonus,
            self.activated,
            self.responded,
            self.attacked,
            self.moved,
            self.passed,
            self.killed,
            self.hit,
            self.attacked_by,
            self.can_transport,
            self.transport_capacity,
            len(self.transporting),
            self.transported_by,
            self.position.x,
            self.position.y,
            self.position.z,
            self.stat.value,
        ]

        for s in STATS_LIST:
            data.append(self.stat == s)

        for w in WEAPON_KEY_LIST:
            data.append(self.weapons[w].ammo if w in self.weapons else 0)

        for d in DEFENSE_KEY_LIST:
            data.append(self.defense[d] if d in self.defense else 0)

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

        self.activated: bool = False
        self.responded: bool = False
        self.attacked: bool = False
        self.moved: bool = False
        self.passed: bool = False
        self.killed: bool = False
        self.hit: bool = False

        self.attacked_by = -1

        if self.hp <= 0:
            self.killed = True
            self.activated = True
            self.hit = False

        for u in self.updates:
            update(self, u)

    def goto(self, destination: Cube) -> None:
        self.position = destination

    def transportLoad(self, figure) -> None:
        if not self.canTransport(figure):
            raise ValueError('cannot load figure')
        self.transporting.append(figure.index)
        figure.transported_by = self.index
        figure.stat = stat('LOADED')

    def transportUnload(self, figure) -> None:
        self.transporting.remove(figure.index)
        figure.transported_by = -1

    def canTransport(self, figure) -> bool:
        if self.killed:
            return False
        if figure.kind == FigureType.VEHICLE:
            return False
        return self.can_transport and len(self.transporting) < self.transport_capacity

    def getKey(self) -> str:
        return f'{self.team}{self.index}'

    def addWeapon(self, w: Weapon) -> None:
        self.weapons[w.wid] = w

    def __repr__(self) -> str:
        return f'{self.name}{self.position}'


def update(f: Figure, data: dict):
    ut = data['type']
    at = data['attribute']

    if ut == 'fixed':
        """Keep the attribute of a figure to a given value."""
        uv = data['value']
        setattr(f, at, uv)

    if ut == 'add':
        """Increase the attribute of a figure by a given value"""
        uv = data['value']
        setattr(f, at, getattr(f, at) + uv)

    if ut == 'remove':
        """Decrease the attribute of a figure by a given value"""
        uv = data['value']
        setattr(f, at, getattr(f, at) - uv)

    if ut == 'clamp':
        """Keep the attribute of a figure between a min and a max value"""
        umin, umax = data['min'], data['max']
        setattr(f, at, min(umax, max(umin, getattr(f, at))))
