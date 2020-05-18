from queue import PriorityQueue

from core.game import GameBoard
from utils.coordinates import Cube, cube_distance

heuristic = cube_distance


def findPath(start: Cube, goal: Cube, board: GameBoard):
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
            new_cost = cost_so_far[current] + board.getCost(current, next)
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
