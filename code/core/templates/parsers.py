from core.figures import FigureType, WEAPON_KEY_LIST, DEFENSE_KEY_LIST, STATUS_KEY_LIST
from core.figures.stats import FIGURES_STATUS_TYPE, FigureStatus
from core.game.terrain import TERRAIN_TYPE, TYPE_TERRAIN, Terrain
from core.templates import TMPL_FIGURES_STATUS_TYPE, TMPL_TERRAIN_TYPE, TMPL_WEAPONS, TMPL_FIGURES


def parse_figure_status():
    for fName, fData in TMPL_FIGURES_STATUS_TYPE.items():
        FIGURES_STATUS_TYPE[fName] = FigureStatus(fData['name'], fData['value'])
        if fName not in STATUS_KEY_LIST:
            STATUS_KEY_LIST.append(fName)


def parse_terrain():
    for tName, tData in TMPL_TERRAIN_TYPE.items():
        level = tData['level']
        terrain = Terrain(
            level,
            tName,
            tData['name'],
            tData['protection'],
            tData['move_cost'][FigureType.INFANTRY],
            tData['move_cost'][FigureType.VEHICLE],
            tData['block_los'],
            tData['color']
        )

        TERRAIN_TYPE[tName] = terrain
        TYPE_TERRAIN[level] = terrain


def parse_weapons():
    weapon_set = []
    for wData in TMPL_WEAPONS.values():
        tag = wData['tag']
        if tag:
            weapon_set.append(tag)

    for k in sorted(list(set(weapon_set))):
        if k not in WEAPON_KEY_LIST:
            WEAPON_KEY_LIST.append(k)


def parse_figures():
    defense_set = []
    for fData in TMPL_FIGURES.values():
        for d in fData['defense']:
            defense_set.append(d)

    for k in sorted(list(set(defense_set))):
        if k not in DEFENSE_KEY_LIST:
            DEFENSE_KEY_LIST.append(k)
