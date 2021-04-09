"""
Source: https://www.redblobgames.com/grids/hexagons/
"""
from typing import List


# we are using offset coordinates with even-q and flat hexagons

def lerp(a: float, b: float, t: float):  # for floats
    return a + (b - a) * t


class Hex:
    __slots__ = ["q", "r"]

    def __init__(self, q: int = 0, r: int = 0, t: tuple = None):
        if t:
            self.q: int = t[0]
            self.r: int = t[1]
        else:
            self.q: int = q
            self.r: int = r

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, Hex):
            return False
        return self.q == other.q and self.r == other.r

    def __lt__(self, other):
        return self.q < other.q and self.r < other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def __str__(self):
        return f'({self.q}, {self.r})'

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r)

    def __len__(self):
        return 2

    def cube(self):
        """Converts offset to cube coordinate system"""
        x = self.q
        z = self.r - (self.q + (self.q % 2)) // 2
        y = -x - z
        return Cube(x, y, z)

    def tuple(self) -> tuple:
        return self.q, self.r

    def round(self):
        return self.cube().round().hex()

    def hex_neighbor(self) -> list:
        parity = self.q % 2
        return [self + direction for direction in hex_directions[parity]]

    def distance(self, other):
        return self.cube().distance(other.cube())

    def line(self, other):
        line = self.cube().line(other.cube())
        return [c.hex() for c in line]

    def hex_range(self, N: int):
        results = self.cube().range(N)
        return [c.hex() for c in results]


class Cube:
    __slots__ = ["x", "y", "z"]

    def __init__(self, x: float = .0, y: float = .0, z: float = .0, t: tuple = None):
        if t:
            self.x: float = t[0]
            self.y: float = t[1]
            self.z: float = t[2]
        else:
            self.x: float = x
            self.y: float = y
            self.z: float = z

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, Cube):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y and self.z < other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __repr__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __str__(self):
        return str(self.hex())

    def __add__(self, other):
        x: float = self.x + other.x
        y: float = self.y + other.y
        z: float = self.z + other.z
        return Cube(x, y, z)

    def __sub__(self, other):
        x: float = self.x - other.x
        y: float = self.y - other.y
        z: float = self.z - other.z
        return Cube(x, y, z)

    def __len__(self):
        return 3

    def hex(self) -> Hex:
        """Converts cube to offset coordinate system"""
        q = self.x
        r = self.z + (self.x + (self.x % 2)) // 2
        return Hex(int(q), int(r))

    def tuple(self) -> tuple:
        return self.hex().tuple()

    def round(self):
        rx = int(round(self.x))
        ry = int(round(self.y))
        rz = int(round(self.z))

        x_diff = abs(rx - self.x)
        y_diff = abs(ry - self.y)
        z_diff = abs(rz - self.z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        else:
            if y_diff > z_diff:
                ry = -rx - rz
            else:
                rz = -rx - ry

        return Cube(rx, ry, rz)

    def neighbor(self) -> List:
        return [self + direction for direction in cube_directions]

    def distance(self, other) -> int:
        return int((abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)) // 2)

    def lerp(self, other, t: float):  # for hexes
        return Cube(
            lerp(self.x, other.x, t),
            lerp(self.y, other.y, t),
            lerp(self.z, other.z, t)
        )

    def line(self, other) -> list:
        n = self.distance(other)

        if n == 0:
            return [self]

        T = 1.0 / n
        eps = Cube(3e-6, 2e-6, 1e-6)

        A = self + eps
        B = other + eps

        results = []
        for i in range(0, n + 1):
            results.append(A.lerp(B, T * i).round())

        return results

    def range(self, N: int) -> list:
        results = []
        for x in range(-N, N + 1):
            for y in range(max(-N, -x - N), min(N, -x + N) + 1):
                z = -x - y
                results.append(self + Cube(x, y, z))
        return results

    def reachable(self, movement: int, obstacles: set) -> set:
        visited = set()  # set of hexes
        visited.add(self)

        fringes = [[self]]  # array of array of hexes

        for k in range(2, movement + 2):
            fringes.append([])
            for h in fringes[k - 2]:
                for neighbor in h.neighbor():
                    if neighbor not in visited and neighbor not in obstacles:
                        visited.add(neighbor)
                        fringes[k - 1].append(neighbor)

        return visited


# Neighbors
cube_directions = [
    Cube(+1, -1, 0), Cube(+1, 0, -1), Cube(0, +1, -1),
    Cube(-1, +1, 0), Cube(-1, 0, +1), Cube(0, -1, +1),
]

hex_directions = [
    [Hex(1, 0), Hex(1, -1), Hex(0, -1), Hex(-1, -1), Hex(-1, 0), Hex(0, 1)],
    [Hex(1, 1), Hex(1, 0), Hex(0, -1), Hex(-1, 0), Hex(-1, 1), Hex(0, 1)],
]
