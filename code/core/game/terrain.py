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

    def __init__(self, name: str, protectionLevel: int, moveCostInf: float, moveCostVehicle: float,
                 blockLos: bool = False):
        self.name = name
        self.protectionLevel = protectionLevel
        self.moveCostInf = moveCostInf
        self.moveCostVehicle = moveCostVehicle
        self.blockLos = blockLos

    def __repr__(self):
        return self.name


TERRAIN_TYPE = [
    Terrain('Open ground', 0, 1., 1.),
    Terrain('Road', 0, .75, .75),
    Terrain('Isolated tree cover', 2, 1., 1., blockLos=True),
    # stops all vehicle from moving
    Terrain('Forest', 4, 1., 1000., blockLos=True),
    # vehicle can move only 1 hexagon on urban terrain
    Terrain('Urban', 0, 1., 6.),
    # solid obstacle
    Terrain('Building', 0, 1000., 1000., blockLos=True),
    # terrain type inside a building
    Terrain('Wooden building', 6, 1., 1000.),
    Terrain('Concrete building', 8, 1., 1000.),
]


class ObstaclesType:
    FOREST = 1
    BUILDING = 2
    ARMORED = 3
