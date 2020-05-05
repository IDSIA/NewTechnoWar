
TOTAL_TURNS = 12

"""From the turn Recorder:"""
# the position in the array is equal to the current turn, starting from 0 (1st) up to 11 (12th) turn
ENDURANCE = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
INTELLIGENCE_ATTACK = [6, 6, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4]
INTELLIGENCE_DEFENSE = [0, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4]


# level of protection from the terrain:
class Terrain:
    """Defines properties of a type of terrain"""

    def __init__(self, name: str, protection_level: int, stop_vehicle: bool = False):
        self.name = name
        self.protection_level = protection_level
        self.stop_vehicle = stop_vehicle


TERRAIN = {
    0: Terrain('Open ground', 0),
    1: Terrain('Isolated tree cover', 2),
    2: Terrain('Forest', 4, True),  # stops all vehicle from moving, unless on a road
    3: Terrain('Wooden building', 6),
    4: Terrain('Concrete building', 8)
}


def hit_score_calculator(
        attack: int,
        terrain: int,
        defense: int,
        status: int,
        endurance: int,
        intelligence: int
):
    return attack - terrain - defense + status + endurance + intelligence
