class Player:

    def __init__(self, name: str, team: str):
        self.name = name
        self.team = team

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseFigure(self, figures: list):
        raise NotImplemented()

    def chooseActionType(self, types: list):
        raise NotImplemented()

    def chooseAction(self, actions: list):
        raise NotImplemented()

    def chooseResponse(self):
        raise NotImplemented()
