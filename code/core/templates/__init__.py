__all__ = [
    "TMPL_WEAPONS",
    "TMPL_FIGURES_STATUS_TYPE",
    "TMPL_FIGURES",
    "TMPL_TERRAIN_TYPE",
    "TMPL_BOARDS",
    "TMPL_SCENARIOS",
    'collect'
]

TMPL_WEAPONS = {}
TMPL_FIGURES_STATUS_TYPE = {}
TMPL_FIGURES = {}
TMPL_TERRAIN_TYPE = {}
TMPL_BOARDS = {}
TMPL_SCENARIOS = {}

from core.templates.collectors import collect

collect()
