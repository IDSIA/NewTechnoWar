"""
Source: https://www.redblobgames.com/grids/hexagons/
"""
from collections import namedtuple

# we are using offset coordinates with even-q and flat hexagons

Hex = namedtuple('Hex', ['q', 'r'])
Cube = namedtuple('Cube', ['x', 'y', 'z'])


# conversions

def cube_to_hex(cube: Cube):
    """Converts cube to offset coordinate system"""
    q = cube.x
    r = cube.z + (cube.x + (cube.x % 2)) // 2
    return Hex(q, r)


def hex_to_cube(h: Hex):
    """Converts offset to cube coordinate system"""
    x = h.q
    z = h.r - (h.q + (h.q % 2)) // 2
    y = -x - z
    return Cube(x, y, z)


def to_hex(pos: tuple):
    """Converts tuple to Hex, [0] is considered column, while [1] row"""
    return Hex(q=pos[0], r=pos[1])


def to_cube(pos: tuple):
    """Converts tuple to Cube, [0] is considered column, while [1] row"""
    return hex_to_cube(to_hex(pos))


# Operations

def cube_add(a: Cube, b: Cube):
    x = a.x + b.x
    y = a.y + b.y
    z = a.z + b.z
    return Cube(x, y, z)


def cube_subtract(a: Cube, b: Cube):
    x = a.x - b.x
    y = a.y - b.y
    z = a.z - b.z
    return Cube(x, y, z)


def hex_add(a: Hex, b: Hex):
    return Hex(a.q + b.q, a.r + b.r)


def hex_subtract(a, b):
    return Hex(a.p2 - b.p2, a.r - b.r)


p1: float = 10 ** 5
p2: int = int(p1)


def cube_round(c: Cube):
    rx = int(c.x * p1 + 0.5) / p2
    ry = int(c.y * p1 + 0.5) / p2
    rz = int(c.z * p1 + 0.5) / p2

    x_diff = abs(rx - c.x)
    y_diff = abs(ry - c.y)
    z_diff = abs(rz - c.z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    else:
        if y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

    return Cube(int(rx), int(ry), int(rz))


def hex_round(h: Hex):
    return cube_to_hex(cube_round(hex_to_cube(h)))


# Neighbors

cube_directions = [
    Cube(+1, -1, 0), Cube(+1, 0, -1), Cube(0, +1, -1),
    Cube(-1, +1, 0), Cube(-1, 0, +1), Cube(0, -1, +1),
]


def cube_neighbor(cube: Cube) -> list:
    return [cube_add(cube, direction) for direction in cube_directions]


hex_directions = [
    [Hex(1, 0), Hex(1, -1), Hex(0, -1), Hex(-1, -1), Hex(-1, 0), Hex(0, 1)],
    [Hex(1, 1), Hex(1, 0), Hex(0, -1), Hex(-1, 0), Hex(-1, 1), Hex(0, 1)],
]


def hex_neighbor(h: Hex) -> list:
    parity = h.q % 2
    return [hex_add(h, direction) for direction in hex_directions[parity]]


# Distances

def cube_distance(a: Cube, b: Cube):
    return int((abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z)) // 2)


def hex_distance(a: Hex, b: Hex):
    ac = hex_to_cube(a)
    bc = hex_to_cube(b)
    return cube_distance(ac, bc)


# Line drawing

def lerp(a: int, b: int, t: float) -> int:  # for floats
    return int((a + (b - a) * t) * p1 + 0.5) // p2


def cube_lerp(a: Cube, b: Cube, t: float):  # for hexes
    return Cube(
        lerp(a.x, b.x, t),
        lerp(a.y, b.y, t),
        lerp(a.z, b.z, t)
    )


def cube_linedraw(a: Cube, b: Cube):
    n = cube_distance(a, b)

    if n == 0:
        return [a]

    eps = Cube(3e-6, 2e-6, 1e-6)

    A = cube_add(a, eps)
    B = cube_add(b, eps)

    results = []
    for i in range(0, n + 1):
        results.append(cube_lerp(A, B, 1.0 / n * i))

    return results


def hex_linedraw(a: Hex, b: Hex):
    line = cube_linedraw(hex_to_cube(a), hex_to_cube(b))
    return [cube_to_hex(h) for h in line]


# Movement range

def cube_range(center: Cube, N: int):
    results = []
    for x in range(-N, N + 1):
        for y in range(max(-N, -x - N), min(N, -x + N) + 1):
            z = -x - y
            results.append(cube_add(center, Cube(x, y, z)))
    return results


def hex_range(center: Hex, N: int):
    results = cube_range(hex_to_cube(center), N)
    return [cube_to_hex(c) for c in results]


# Obstacles

def cube_reachable(start: Cube, movement, obstacles: set):
    visited = set()  # set of hexes
    visited.add(start)

    fringes = [[start]]  # array of array of hexes

    for k in range(2, movement + 2):
        fringes.append([])
        for h in fringes[k - 2]:
            for neighbor in cube_neighbor(h):
                if neighbor not in visited and neighbor not in obstacles:
                    visited.add(neighbor)
                    fringes[k - 1].append(neighbor)

    return visited
