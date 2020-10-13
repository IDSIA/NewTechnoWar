__all__ = [
    "Figure",
    "Tank", "APC", "Infantry", "Exoskeleton", "Sniper", "Civilian",
    "buildFigure",
    "FigureStatus", "stat",

    "Weapon",
    "Cannon", "AssaultRifle", "MachineGun", "AntiTank", "Mortar", "Grenade", "SmokeGrenade", "SniperRifle",
    "WEAPON_KEY_LIST", "DEFENSE_KEY_LIST",
    "setup_weapons",
]

from core.figures.figure import Figure, Tank, APC, Infantry, Exoskeleton, Sniper, Civilian

from core.figures.lists import WEAPON_KEY_LIST, DEFENSE_KEY_LIST
from core.figures.stats import FigureStatus, stat
from core.figures.weapons import Weapon, Cannon, AssaultRifle, MachineGun, AntiTank, Mortar, Grenade, SmokeGrenade, \
    SniperRifle
from core.templates import TMPL_FIGURES, TMPL_WEAPONS
from utils import INFINITE


def setup_weapons(figure: Figure, values: dict) -> None:
    for wName, wData in values.items():
        tw = TMPL_WEAPONS[wName]
        tw['ammo'] = INFINITE if wData == 'inf' else wData
        tw['ammo_max'] = tw['ammo']

        w = Weapon()
        for kw, vw in tw.items():
            if kw == 'atk':
                setattr(w, 'atk_normal', vw['normal'])
                setattr(w, 'atk_response', vw['response'])
            else:
                setattr(w, kw, vw)
        figure.addWeapon(w)


def buildFigure(type: str, position: tuple, team: str, status: FigureStatus = None) -> Figure:
    t = TMPL_FIGURES[type]
    s = status if status else stat('NO_EFFECT')

    figure = Figure(position, type, team, t['kind'], s)

    for k, v in t.items():
        if k == 'weapons':
            setup_weapons(figure, v)
        else:
            setattr(figure, k, v)

    return figure
