from core.actions.basics import ActionFigure, Action
from core.figures import Figure


class Pass:
    """Group of actions that passes the turn to the opposite team."""

    def __repr__(self):
        return 'Pass'

    def __str__(self):
        return 'Pass'


class PassTeam(Pass, Action):
    """Action that does absolutely nothing."""

    def __init__(self, team: str):
        super().__init__(team)

    def __repr__(self):
        return f'{Action.__repr__(self)} {Pass.__repr__(self)}'

    def __str__(self):
        return f'{Action.__str__(self)} {Pass.__str__(self)}'


class PassFigure(Pass, ActionFigure):
    """Action that just activate a figure, and does nothing else."""

    def __init__(self, figure: Figure):
        super().__init__(figure=figure)

    def __repr__(self):
        return f'{ActionFigure.__repr__(self)} {Pass.__repr__(self)}'

    def __str__(self):
        return f'{ActionFigure.__str__(self)} {Pass.__str__(self)}'
