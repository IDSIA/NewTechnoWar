from collections import namedtuple
from typing import Dict

"""Current status of a figure"""
FigureStatus = namedtuple('FigureStatus', ['name', 'value'])

FIGURES_STATUS_TYPE: Dict[str, FigureStatus] = {}
