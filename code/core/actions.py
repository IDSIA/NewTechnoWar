from core.figures import Figure


class Action:

    def __init__(self, figure: Figure):
        self.figure = figure


class Move(Action):

    def __init__(self, figure: Figure, destination: tuple):
        super().__init__(figure)
        self.destination = destination


class Shoot(Action):

    def __init__(self, figure: Figure, target: Figure):
        super().__init__(figure)
        self.target = target


class Respond(Action):

    def __init__(self, figure: Figure, target: Figure):
        super().__init__(figure)
        self.target = target
