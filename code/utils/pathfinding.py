from queue import PriorityQueue

from core import FigureType
from core.figures import Figure
from core.game import GameBoard
from utils.coordinates import Cube, cube_distance

heuristic = cube_distance


def reachablePath(figure: Figure, board: GameBoard, max_cost: int):
    """This uses Uniform Cost Search."""
    start = figure.position

    visited = set()
    visited.add(start)

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        _, current = frontier.get()
        visited.add(current)

        for next in board.getNeighbors(current):
            new_cost = cost_so_far[current] + board.getMovementCost(next, figure.kind)

            if new_cost > max_cost:
                continue

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put((priority, next))
                came_from[next] = current

    paths = []
    for goal in visited:
        x = goal
        path = [goal]
        # paths.append((cost_so_far[goal], path))
        paths.append(path)
        while x:
            x = came_from[x]
            if x:
                path.insert(0, x)

    return visited, paths


def findPath(start: Cube, goal: Cube, board: GameBoard, kind: FigureType):
    """This uses A*"""
    frontier = PriorityQueue()
    frontier.put((0, start))

    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for next in board.getNeighbors(current):
            new_cost = cost_so_far[current] + board.getMovementCost(next, kind)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put((priority, next))
                came_from[next] = current

    path = [goal]
    x = goal
    while x:
        x = came_from[x]
        if x:
            path.insert(0, x)

    return path
