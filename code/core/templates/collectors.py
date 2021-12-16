import logging
from ntpath import join
import os
from collections.abc import Mapping
from posixpath import abspath

import yaml

from core.const import INFINITE
from core.templates import TMPL_WEAPONS, TMPL_FIGURES_STATUS_TYPE, TMPL_FIGURES, TMPL_TERRAIN_TYPE, TMPL_BOARDS, TMPL_SCENARIOS
from core.templates.parsers import parse_terrain, parse_figure_status, parse_weapons, parse_figures
from utils.copy import deepcopy

logger = logging.getLogger(__name__)

COLLECTED: dict = {}


def collect_weapons(data: dict) -> None:
    """Template collector for weapons."""
    for name, wData in data['weapon'].items():
        TMPL_WEAPONS[name] = wData
        logger.info(f'collected weapon: {name}')


def collect_figure_status(data: dict) -> None:
    """Template collector for figure statuses."""
    for name, fData in data['status'].items():
        TMPL_FIGURES_STATUS_TYPE[name] = fData
        logger.info(f'collected figure status: {name}')


def collect_figure(data: dict) -> None:
    """Template collector for figures."""
    for name, fData in data['figure'].items():
        TMPL_FIGURES[name] = fData
        logger.info(f'collected figure: {name}')


def collect_terrain_type(data: dict) -> None:
    """Template collector for terrain types."""
    for name, tData in data['terrain'].items():
        tData['level'] = len(TMPL_TERRAIN_TYPE)
        tData['key'] = name
        TMPL_TERRAIN_TYPE[name] = tData
        logger.info(f'collected terrain: {name}')


def collect_board(data: dict) -> None:
    """Template collector for boards."""
    for name, bData in data['board'].items():
        TMPL_BOARDS[name] = bData
        filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
        if os.path.exists(filename):
            os.remove(filename)
        logger.info(f'collected board: {name}')


def collect_scenario(data: dict) -> None:
    """Template collector for scenarios."""
    for name, sData in data['scenario'].items():
        TMPL_SCENARIOS[name] = sData
        filename = os.path.join(os.getcwd(), 'cache', f'{name}.png')
        if os.path.exists(filename):
            os.remove(filename)
        logger.info(f'collected board: {name}')


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
        logger.info(f'upgraded template: {k}')


def collect(config_dir: str = None) -> None:
    """Main template collector function."""
    global COLLECTED

    newItems = set()

    config_dirs = [
        config_dir,
        os.path.join('.', 'config'),
        os.path.join('..', 'config'),
        os.path.join(os.getcwd(), 'config'),
        os.path.join(os.getcwd(), '..', 'config'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'config'),
    ]

    for dir in config_dirs:
        if dir and os.path.exists(dir) and os.path.isdir(dir):
            config_dir = dir
            break

    logger.info(f'config dir: {config_dir}')

    SUB_DIRS = ['terrains', 'maps', 'weapons', 'status', 'figures', 'scenarios', '.']

    for directory in SUB_DIRS:
        path = os.path.join(config_dir, directory)
        logger.info(f'reading content of {path}')

        for name in os.listdir(path):
            filename = os.path.join(path, name)
            editTime = os.path.getmtime(filename)

            if os.path.isdir(filename):
                continue
            if filename in COLLECTED and COLLECTED[filename] >= editTime:
                continue

            COLLECTED[filename] = editTime

            logger.info(f'collecting from {filename}')
            with open(filename) as f:
                data = yaml.safe_load(f)

                if 'terrain' in data:
                    collect_terrain_type(data)
                    newItems.add('terrain')

                if 'board' in data:
                    collect_board(data)
                    newItems.add('board')

                if 'weapon' in data:
                    collect_weapons(data)
                    newItems.add('weapon')

                if 'status' in data:
                    collect_figure_status(data)
                    newItems.add('status')

                if 'figure' in data:
                    collect_figure(data)
                    newItems.add('figure')

                if 'scenario' in data:
                    collect_scenario(data)
                    newItems.add('scenario')

    if not newItems:
        logger.info('nothing new to collect')
        return

    # upgrade the templates if they are based on other template (templateception!)
    if 'weapon' in newItems:
        template_upgrade(TMPL_WEAPONS)
    if 'status' in newItems:
        template_upgrade(TMPL_FIGURES_STATUS_TYPE)
    if 'figure' in newItems:
        template_upgrade(TMPL_FIGURES)
    if 'terrain' in newItems:
        template_upgrade(TMPL_TERRAIN_TYPE)
    if 'board' in newItems:
        template_upgrade(TMPL_BOARDS)
    if 'scenario' in newItems:
        template_upgrade(TMPL_SCENARIOS)

    # fix for figure templates (type -> kind, hp_max = hp)
    if 'figure' in newItems:
        for k in TMPL_FIGURES.keys():
            TMPL_FIGURES[k]['kind'] = TMPL_FIGURES[k].pop('type', None)
            TMPL_FIGURES[k]['hp_max'] = TMPL_FIGURES[k]['hp']

    # fix for weapon templates (max_range -> inf)
    if 'weapon' in newItems:
        for k in TMPL_WEAPONS.keys():
            TMPL_WEAPONS[k]['max_range'] = \
                INFINITE if TMPL_WEAPONS[k]['max_range'] == 'inf' else TMPL_WEAPONS[k]['max_range']

    # parse templates to populate basic containers
    if 'terrain' in newItems:
        parse_terrain()
    if 'status' in newItems:
        parse_figure_status()
    if 'weapon' in newItems:
        parse_weapons()
    if 'figure' in newItems:
        parse_figures()
