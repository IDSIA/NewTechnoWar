from core.actions.basics import Action


class Wait(Action):
    """Action that does literally nothing."""

    def __init__(self, team: str):
        super().__init__(team)

    def __repr__(self):
        return f'{Action.__repr__(self)} {"":10}: Waits'

    def __str__(self):
        return f'{Action.__str__(self)} {"":10}: Waits'
