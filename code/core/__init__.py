RED = 'red'
BLUE = 'blue'

ACTION_ATTACK = 0
ACTION_MOVE = 1

TOTAL_TURNS = 12

"""From the turn Recorder:"""
# the position in the array is equal to the current turn, starting from 0 (1st) up to 11 (12th) turn
ENDURANCE = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
INTELLIGENCE_ATTACK = [6, 6, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4]
INTELLIGENCE_DEFENSE = [0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4]


class FigureType:
    """Defines the possible types of a Figure"""
    OTHER = 0
    INFANTRY = 1
    VEHICLE = 2


# level of protection from the terrain:
class Terrain:
    """Defines properties of a type of terrain"""

    OPEN_GROUND = 0
    ROAD = 1
    ISOLATED_TREE = 2
    # TODO: how to model 'edge of the forest'? This should be something that gives no cover but protection only
    FOREST = 3
    URBAN = 4
    BUILDING = 5
    WOODEN_BUILDING = 6
    CONCRETE_BUILDING = 7

    def __init__(self, name: str, protectionLevel: int, moveCostInf: float, moveCostVehicle: float):
        self.name = name
        self.protectionLevel = protectionLevel
        self.moveCostInf = moveCostInf
        self.moveCostVehicle = moveCostVehicle


TERRAIN_TYPE = [
    Terrain('Open ground', 0, 1., 1.),
    Terrain('Road', 0, .75, .75),
    Terrain('Isolated tree cover', 2, 1., 1.),
    # stops all vehicle from moving
    Terrain('Forest', 4, 1., 1000.),
    # vehicle can move only 1 hexagon on urban terrain
    Terrain('Urban', 0, 1., 6.),
    # solid obstacle
    Terrain('Building', 0, 1000., 1000.),
    # terrain type inside a building
    Terrain('Wooden building', 6, 1., 1000.),
    Terrain('Concrete building', 8, 1., 1000.),
]

TERRAIN_OBSTACLES_TO_LOS = (Terrain.FOREST, Terrain.BUILDING, Terrain.ISOLATED_TREE)


class ObstaclesType:
    FOREST = 1
    BUILDING = 2
    ARMORED = 3


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
