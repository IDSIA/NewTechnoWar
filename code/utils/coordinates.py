"""
Source: https://www.redblobgames.com/grids/hexagons/
"""
from collections import namedtuple
import math

# we are using offset coordinates with oddq and flat hexs

Hex = namedtuple('Hex', ['col', 'row'])
Cube = namedtuple('Cube', ['x', 'y', 'z'])


# conversions


def cube_to_hex(cube: Cube):
    """Converts cube to offset coordinate system"""
    col = cube.x
    row = cube.z + (cube.x - (cube.x % 2))/2
    return Hex(col, row)


def hex_to_cube(hex: Hex):
    """Converts offset to cube coordinate system"""
    x = hex.col
    z = hex.row - (hex.col - (hex.col % 1))/2
    y = -x-z
    return Cube(x, y, z)


# Operations


def cube_add(a: Cube, b: Cube):
    x = a.x + b.x
    y = a.y + b.y
    z = a.z + b.z
    return Cube(x, y, z)


def hex_add(a: Hex, b: Hex):
    return Hex(a.col + b.col, a.row + b.row)


def cube_round(c: Cube):
    rx = round(c.x)
    ry = round(c.y)
    rz = round(c.z)

    x_diff = abs(rx - c.x)
    y_diff = abs(ry - c.y)
    z_diff = abs(rz - c.z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry-rz
    elif y_diff > z_diff:
        ry = -rx-rz
    else:
        rz = -rx-ry

    return Cube(rx, ry, rz)


def hex_round(hex: Hex):
    return cube_to_hex(cube_round(hex_to_cube(hex)))


# Neighbors


cube_directions = [
    Cube(+1, -1, 0), Cube(+1, 0, -1), Cube(0, +1, -1),
    Cube(-1, +1, 0), Cube(-1, 0, +1), Cube(0, -1, +1),
]


def cube_direction(direction):
    return cube_directions[direction]


def cube_neighbor(cube, direction):
    return cube_add(cube, cube_direction(direction))


hex_directions = [
    [Hex(1, 0), Hex(1, -1), Hex(0, -1), Hex(-1, -1), Hex(-1, 0), Hex(0, 1)],
    [Hex(1, 1), Hex(1, 0), Hex(0, -1), Hex(-1, 0), Hex(-1, 1), Hex(0, 1)],
]


def hex_neighbor(hex: Hex, direction):
    parity = hex.col % 2
    d = hex_directions[parity][direction]
    return hex_add(hex, d)


# Distances

def cube_distance(a: Cube, b: Cube):
    return (abs(a.x-b.x) + abs(a.y-b.y)+abs(a.z-b.z))/2


def hex_distance(a: Hex, b: Hex):
    ac = hex_to_cube(a)
    bc = hex_to_cube(b)
    return cube_distance(ac, bc)


# Line drawing


def lerp(a: int, b: int, t: int):  # for floats
    return a + (b - a) * t


def cube_lerp(a: Cube, b: Cube, t: int):  # for hexes
    return Cube(
        lerp(a.x, b.x, t),
        lerp(a.y, b.y, t),
        lerp(a.z, b.z, t)
    )


def cube_linedraw(a: Cube, b: Cube):
    n = cube_distance(a, b)

    eps = Cube(1e-6, 2e-6, 3e-6)

    A = cube_add(a, eps)
    B = cube_add(b, eps)

    results = []
    for i in range(0, n + 1):
        results.append(cube_round(cube_lerp(A, B, 1.0 / n * i)))
    return results


def hex_linedraw(a: Hex, b: Hex):
    return cube_linedraw(hex_to_cube(a), hex_to_cube(b))


# Movement range


def cube_movement(center: Cube, N: int):
    results = []
    for x in range(-N, N+1):
        for y in range(max(-N, -x-N), min(N, -x+N) + 1):
            z = -x-y
            results.append(cube_add(center, Cube(x, y, z)))
    return results


def hex_movement(center: Hex, N: int):
    results = cube_movement(hex_to_cube(center), N)
    return [cube_to_hex(c) for c in results]


# Obstacles

def cube_reachable(start: Cube, movement, obstacles: set()):
    visited = set()  # set of hexes
    visited.add(start)

    fringes = []  # array of array of hexes
    fringes.append([start])

    for k in range(2, movement+1):
        fringes.append([])
        for hex in fringes[k-1]:
            for dir in (0, 6):
                neighbor = cube_neighbor(hex, dir)
                if neighbor not in visited and neighbor not in obstacles:
                    visited.add(neighbor)
                    fringes[k].append(neighbor)

    return visited


def hex_reachable(start: Hex, movement, obstacles: set()):
    visited = set()  # set of hexes
    visited.add(start)

    fringes = []  # array of array of hexes
    fringes.append([start])

    for k in range(2, movement+1):
        fringes.append([])
        for hex in fringes[k-1]:
            for dir in (0, 6):
                neighbor = hex_neighbor(hex, dir)
                if neighbor not in visited and neighbor not in obstacles:
                    visited.add(neighbor)
                    fringes[k].append(neighbor)

    return visited
