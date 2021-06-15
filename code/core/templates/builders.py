from core.const import INFINITE
from core.templates import TMPL_WEAPONS, TMPL_FIGURES
from core.figures import Figure, Weapon, FigureStatus, stat


def setupWeapons(figure: Figure, values: dict) -> None:
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


def buildFigure(type: str, position: tuple, team: str, name: str = None, status: FigureStatus = None) -> Figure:
    t = TMPL_FIGURES[type]
    n = name if name else type
    s = status if status else stat('NO_EFFECT')

    figure = Figure(position, n, team, t['kind'], s)

    for k, v in t.items():
        if k == 'weapons':
            setupWeapons(figure, v)
        elif k == 'update':
            for uData in v:
                figure.updates.append(uData)
        else:
            setattr(figure, k, v)

    return figure
