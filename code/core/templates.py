__all__ = [
    "TMPL_WEAPONS",
    "TMPL_FIGURES_STATUS_TYPE",
    "TMPL_FIGURES",
    "TMPL_TERRAIN_TYPE",
    "TMPL_BOARDS",
    "TMPL_SCENARIOS",
]

from collections.abc import Mapping
import os
import yaml

from core.figures import FIGURES_STATUS_TYPE, FigureStatus
from core.game.terrain import TERRAIN_TYPE, Terrain
from utils.copy import deepcopy

TMPL_WEAPONS = {}
TMPL_FIGURES_STATUS_TYPE = {}
TMPL_FIGURES = {}
TMPL_TERRAIN_TYPE = {}
TMPL_BOARDS = {}
TMPL_SCENARIOS = {}


def collect_weapons(data: dict):
    """Template collector for weapons."""
    for wName, wData in data['weapon'].items():
        TMPL_WEAPONS[wName] = wData


def collect_figure_status(data: dict):
    """Template collector for figure statuses."""
    for fName, fData in data['status'].items():
        TMPL_FIGURES_STATUS_TYPE[fName] = fData


def collect_figure(data: dict):
    """Template collector for figures."""
    for fName, fData in data['figure'].items():
        TMPL_FIGURES[fName] = fData


def collect_terrain_type(data: dict):
    """Template collector for terrain types."""
    for wName, tData in data['terrain'].items():
        TMPL_TERRAIN_TYPE[wName] = tData


def collect_board(data: dict):
    """Template collector for boards."""
    for name, bData in data['board'].items():
        TMPL_BOARDS[name] = bData


def collect_scenario(data: dict):
    """Template collector for scenarios."""
    for sName, sData in data['scenario'].items():
        TMPL_SCENARIOS[sName] = sData


def update(d: dict, u: Mapping):
    """Updates a dictionary 'd' based on a mapping (another dictionary) 'u'."""
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def template_upgrade(data: dict):
    """Checks for other templates in the same dictionary, if found update the template based on another template."""
    for k in data.keys():
        if k == 'template':
            continue

        if 'template' in data[k]:
            tmpl = data[data[k]['template']]
        elif 'template' not in data:
            continue
        else:
            tmpl = data['template']

        data[k] = update(deepcopy(tmpl), data[k])


def parse_figure_status():
    for fName, fData in TMPL_FIGURES_STATUS_TYPE.items():
        FIGURES_STATUS_TYPE[fName] = FigureStatus(fData['name'], fData['value'])


def parse_terrain():
    for name, tData in TMPL_TERRAIN_TYPE.items():
        TERRAIN_TYPE[name] = Terrain(
            len(TERRAIN_TYPE),
            tData['name'],
            tData['protection'],
            tData['move_cost']['infantry'],
            tData['move_cost']['vehicle'],
            tData['block_los']
        )


COLLECTED: bool = False


def collect():
    """Main template collector function."""
    global COLLECTED

    if COLLECTED:
        return

    MAIN_DIR = 'config'
    SUB_DIRS = ['terrains', 'maps', 'weapons', 'status', 'figures', 'scenarios']

    for directory in SUB_DIRS:
        path = os.path.join(MAIN_DIR, directory)
        for name in os.listdir(path):
            with open(os.path.join(path, name)) as f:
                data = yaml.safe_load(f)

                if 'terrain' in data:
                    collect_terrain_type(data)

                if 'board' in data:
                    collect_board(data)

                if 'weapon' in data:
                    collect_weapons(data)

                if 'status' in data:
                    collect_figure_status(data)

                if 'figure' in data:
                    collect_figure(data)

                if 'scenario' in data:
                    collect_scenario(data)

    # upgrade the templates if they are based on other template (templateception!)
    template_upgrade(TMPL_WEAPONS)
    template_upgrade(TMPL_FIGURES_STATUS_TYPE)
    template_upgrade(TMPL_FIGURES)
    template_upgrade(TMPL_TERRAIN_TYPE)
    template_upgrade(TMPL_BOARDS)
    template_upgrade(TMPL_SCENARIOS)

    # fix for figure templates (type -> kind, hp_max = hp)
    for k in TMPL_FIGURES.keys():
        TMPL_FIGURES[k]['kind'] = TMPL_FIGURES[k].pop('type', None)
        TMPL_FIGURES[k]['hp_max'] = TMPL_FIGURES[k]['hp']

    # parse templates to populate basic containers
    parse_terrain()

    COLLECTED = True


collect()
