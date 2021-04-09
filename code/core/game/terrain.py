class Terrain:
    """Defines properties of a type of terrain"""

    OPEN_GROUND = 0
    ROAD = 1
    ISOLATED_TREE = 2
    FOREST = 3
    WOODEN_BUILDING = 4
    CONCRETE_BUILDING = 5

    def __init__(self, name: str, protectionLevel: int, moveCostInf: float, moveCostVehicle: float,
                 blockLos: bool = False):
        self.name = name
        self.protectionLevel = protectionLevel
        self.moveCostInf = moveCostInf
        self.moveCostVehicle = moveCostVehicle
        self.blockLos = blockLos

    def __repr__(self):
        return self.name


# level of protection from the terrain:
TERRAIN_TYPE = [
    Terrain('Open ground', 0, 1., 1.),
    Terrain('Road', 0, .75, .75),
    Terrain('Isolated tree cover', 2, 1., 1., blockLos=True),
    # stops all vehicle from moving
    Terrain('Forest', 4, 1., 1000., blockLos=True),
    Terrain('Wooden building', 6, 1., 1., blockLos=True),
    Terrain('Concrete building', 8, 1., 6., blockLos=True),
]
