from typing import Dict


class Terrain:
    """Defines properties of a type of terrain"""

    def __init__(self, level: int = -1, key: str = '', name: str = '', protectionLevel: int = 0,
                 moveCostInf: float = 1.0, moveCostVehicle: float = 1.0, blockLos: bool = False,
                 color: str = '#ffffff'):
        self.key = key
        self.level = level
        self.name = name
        self.protectionLevel = protectionLevel
        self.moveCostInf = moveCostInf
        self.moveCostVehicle = moveCostVehicle
        self.blockLos = blockLos
        self.color = color

    def __repr__(self):
        return self.name


TERRAIN_TYPE: Dict[str, Terrain] = {}
TYPE_TERRAIN: Dict[int, Terrain] = {}
