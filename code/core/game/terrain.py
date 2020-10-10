class Terrain:
    """Defines properties of a type of terrain"""

    OPEN_GROUND = 0
    ROAD = 1
    ISOLATED_TREE = 2
    FOREST = 3
    WOODEN_BUILDING = 4
    CONCRETE_BUILDING = 5

    def __init__(self, level: int = -1, name: str = '', protectionLevel: int = 0, moveCostInf: float = 1.0,
                 moveCostVehicle: float = 1.0, blockLos: bool = False):
        self.level = level
        self.name = name
        self.protectionLevel = protectionLevel
        self.moveCostInf = moveCostInf
        self.moveCostVehicle = moveCostVehicle
        self.blockLos = blockLos

    def __repr__(self):
        return self.name


# level of protection from the terrain:
TERRAIN_TYPE = [
    Terrain(0, 'Open ground', 0, 1., 1.),
    Terrain(1, 'Road', 0, .75, .75),
    Terrain(2, 'Isolated tree cover', 2, 1., 1., blockLos=True),
    # stops all vehicle from moving
    Terrain(3, 'Forest', 4, 1., 1000., blockLos=True),
    Terrain(4, 'Wooden building', 6, 1., 1., blockLos=True),
    Terrain(5, 'Concrete building', 8, 1., 6., blockLos=True),
]
