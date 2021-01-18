from core.figures import Figure

# TODO: add method to EXECUTE the action directly on an Action object

class Action:
    """Basic action class"""

    __slots__ = ['team']

    def __init__(self, team: str):
        """
        :param team:    name of the team
        """
        self.team = team

    def __repr__(self):
        return f'{self.team:5}:'

    def __str__(self):
        return f'{self.team.upper():5}:'


class ActionFigure(Action):
    """Basic action for Figures."""

    __slots__ = ['figure_id', 'figure_name']

    def __init__(self, figure: Figure):
        """
        :param figure:  Figure that performs the action
        """
        super().__init__(figure.team)
        self.figure_id = figure.index
        self.figure_name = figure.name

    def __repr__(self):
        return f'{super().__repr__()} {self.figure_name:10}'

    def __str__(self):
        return f'{super().__str__()} {self.figure_name:10}'

