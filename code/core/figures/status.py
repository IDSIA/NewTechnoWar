class FigureStatus:
    """Current status of a figure"""

    __slots__ = ['name', 'value']

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


# units cannot be seen or be a target
HIDDEN = FigureStatus('Hidden', 0)
# unit default status
NO_EFFECT = FigureStatus('No effect', 0)
# the unit has already used its ability to move this turn
IN_MOTION = FigureStatus('In motion', 3)
# if the troops are on an upper flor of a house (scenario specified)
UPSTAIRS = FigureStatus('Upstairs', 3)
# if the troops have already been targeted by a shot this turn
UNDER_FIRE = FigureStatus('Under fire', -1)
# no friendly troop within 4 hexagons
CUT_OFF = FigureStatus('Cut off', 3)
