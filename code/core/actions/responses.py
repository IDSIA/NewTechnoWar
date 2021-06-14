from core.actions.attacks import AttackFigure
from core.actions.passes import PassTeam
from core.figures import Figure, Weapon


class Response:
    """Group of actions that are used in response of actions."""

    def __repr__(self):
        return 'in response'

    def __str__(self):
        return 'in response'


class NoResponse(PassTeam, Response):
    """Response that does nothing and does not activate a unit."""

    def __init__(self, team: str):
        PassTeam.__init__(self, team)

    def __repr__(self):
        return f'{PassTeam.__repr__(self)} {Response.__repr__(self)}'

    def __str__(self):
        return f'{PassTeam.__str__(self)} {Response.__str__(self)}'


class AttackResponse(AttackFigure, Response):
    """Similar to Attack, but created only after a Attack Action."""

    def __init__(self, figure: Figure, target: Figure, guard: Figure, weapon: Weapon, los: list, lof: list):
        """
        :param figure:  Figure that performs the action
        :param target:  Figure target of the action
        :param guard:   Figure that can see the target directly
        :param weapon:  weapon used by the attacker
        :param los:     direct line of sight on target (from who can see it)
        :param lof:     direct line of fire on target (from the attacker)
        """
        super().__init__(figure, target, guard, weapon, los, lof)

    def __repr__(self):
        return f'{AttackFigure.__repr__(self)} {Response.__repr__(self)}'

    def __str__(self):
        return f'{AttackFigure.__str__(self)} {Response.__str__(self)}'
