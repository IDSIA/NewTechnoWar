import os
from collections.abc import Mapping

import yaml

from core.const import INFINITE
from core.templates import TMPL_WEAPONS, TMPL_FIGURES_STATUS_TYPE, TMPL_FIGURES, TMPL_TERRAIN_TYPE, TMPL_BOARDS, \
    TMPL_SCENARIOS
from core.templates.parsers import parse_terrain, parse_figure_status, parse_weapons, parse_figures
from utils.copy import deepcopy

COLLECTED: bool = False


def collect_weapons(data: dict) -> None:
    """Template collector for weapons."""
    for wName, wData in data['weapon'].items():
        TMPL_WEAPONS[wName] = wData


def collect_figure_status(data: dict) -> None:
    """Template collector for figure statuses."""
    for fName, fData in data['status'].items():
        TMPL_FIGURES_STATUS_TYPE[fName] = fData


def collect_figure(data: dict) -> None:
    """Template collector for figures."""
    for fName, fData in data['figure'].items():
        TMPL_FIGURES[fName] = fData


def collect_terrain_type(data: dict) -> None:
    """Template collector for terrain types."""
    for wName, tData in data['terrain'].items():
        TMPL_TERRAIN_TYPE[wName] = tData


def collect_board(data: dict) -> None:
    """Template collector for boards."""
    for name, bData in data['board'].items():
        TMPL_BOARDS[name] = bData


def collect_scenario(data: dict) -> None:
    """Template collector for scenarios."""
    for sName, sData in data['scenario'].items():
        TMPL_SCENARIOS[sName] = sData


def update(d: dict, u: Mapping) -> dict:
    """Updates a dictionary 'd' based on a mapping (another dictionary) 'u'."""
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def template_upgrade(data: dict) -> None:
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


def collect() -> None:
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

    # fix for weapon templates (max_range -> inf)
    for k in TMPL_WEAPONS.keys():
        TMPL_WEAPONS[k]['max_range'] = \
            INFINITE if TMPL_WEAPONS[k]['max_range'] == 'inf' else TMPL_WEAPONS[k]['max_range']

    # parse templates to populate basic containers
    parse_terrain()
    parse_figure_status()
    parse_weapons()
    parse_figures()

    COLLECTED = True
