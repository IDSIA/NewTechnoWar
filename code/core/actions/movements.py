from typing import List

from core.actions.basics import ActionFigure
from core.figures import Figure
from utils.coordinates import Cube, cube_to_hex


class Move(ActionFigure):
    """Action to move a Figure to the destination."""

    __slots__ = ['position', 'path', 'destination']

    def __init__(self, figure: Figure, path: List[Cube]):
        """
        :param figure:  Figure that performs the action
        :param path:    path from current position to destination
        """
        super().__init__(figure)
        self.position: Cube = figure.position
        self.path: List[Cube] = path
        self.destination: Cube = path[-1]

    def __repr__(self):
        return f'{super().__repr__()}: Move to {self.destination}'

    def __str__(self):
        return f'{super().__str__()}: Moved to {cube_to_hex(self.destination)}'


class LoadInto(Move):
    """Action to load a Figure in a transporter at the destination."""

    __slots__ = ['transporter_id', 'transporter_name']

    def __init__(self, figure: Figure, path: list, transporter: Figure):
        """
        :param figure:          Figure that performs the action
        :param path:            path from current position to destination
        :param transporter:     Figure to use as a transporter
        """
        super().__init__(figure, path)
        self.transporter_id = transporter.index
        self.transporter_name = transporter.name

    def __repr__(self):
        return f'{super().__repr__()} and load into {self.transporter_name}'

    def __str__(self):
        return f'{super().__str__()} and loaded into {self.transporter_name}'
