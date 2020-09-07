from core.const import RED, BLUE
from utils.coordinates import Cube

# static parts of the game

"""From the turn Recorder:"""
# the position in the array is equal to the current turn, starting from 0 (1st) up to 11 (12th) turn
ENDURANCE = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
ENDURANCE_EXO = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

INTELLIGENCE_ATTACK = [6, 6, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4]
INTELLIGENCE_DEFENSE = [0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4]

MAX_SMOKE = 2
CUTOFF_RANGE = 4


def hitScoreCalculator(
        attack: int,
        terrain: int,
        defense: int,
        status: int,
        endurance: int,
        intelligence: int
):
    # TODO: meaning of the "+/-" symbol
    #       if your opponent is moving, it is harder to hit him -> -END
    #       if you are in a better position (higher) than you opponent, it is easier to hit him -> +END
    return attack - terrain - defense + status + endurance + intelligence


def missMatrixRed(v: int) -> Cube:
    # range 2
    if v in [1, 3, 6, 12, 20]:
        return Cube(+2, -2, +0)
    if v in [2, 7, 13]:
        return Cube(+2, +0, -2)
    if v in [4, 5, 11]:
        return Cube(+0, -2, +2)
    if v == 8:
        return Cube(+0, +2, -2)
    if v == 9:
        return Cube(-2, +2, +0)
    if v == 10:
        return Cube(-2, +0, +2)
    # range 1
    if v == 14:
        return Cube(+0, +1, -1)
    if v == 15:
        return Cube(-1, +1, +0)
    if v == 16:
        return Cube(-1, +0, +1)
    if v == 17:
        return Cube(+0, -1, +1)
    if v == 18:
        return Cube(+1, -1, +0)
    if v == 19:
        return Cube(+1, +0, -1)

    # center
    return Cube(+0, +0, +0)


def missMatrixBlue(v: int) -> Cube:
    # range 2
    if v in [1, 3, 6, 12, 20]:
        return Cube(-2, +2, +0)
    if v in [2, 7, 13]:
        return Cube(+0, +2, -2)
    if v in [4, 5, 11]:
        return Cube(-2, +0, +2)
    if v == 8:
        return Cube(+2, +0, -2)
    if v == 9:
        return Cube(+2, -2, +0)
    if v == 10:
        return Cube(+0, -2, +2)
    # range 1
    if v == 14:
        return Cube(+0, -1, +1)
    if v == 15:
        return Cube(+1, -1, +0)
    if v == 16:
        return Cube(+1, +0, -1)
    if v == 17:
        return Cube(+0, +1, -1)
    if v == 18:
        return Cube(-1, +1, +0)
    if v == 19:
        return Cube(-1, +0, +1)

    # center
    return Cube(+0, +0, +0)


MISS_MATRIX = {
    RED: missMatrixRed,
    BLUE: missMatrixBlue
}
