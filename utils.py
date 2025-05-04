import pygame
from collections import defaultdict

def compress_rects(rects):
    """
    Compress a list of pygame.Rect objects into fewer rectangles that cover the same area.

    Args:
        rects (list): A list of pygame.Rect objects.

    Returns:
        list: A list of compressed pygame.Rect objects.
    """
    if not rects:
        return []

    # Use a spatial grid to group rectangles
    grid_size = 64
    buckets = defaultdict(list)

    # Place rectangles into grid buckets
    for rect in rects:
        grid_x = rect.x // grid_size
        grid_y = rect.y // grid_size
        buckets[(grid_x, grid_y)].append(rect)

    # Merge rectangles within each bucket
    merged_rects = []
    for bucket_rects in buckets.values():
        merged_rects.extend(merge_all_rects(bucket_rects))

    # Perform a final merge across all merged rectangles
    return merge_all_rects(merged_rects)

def merge_all_rects(rects):
    """
    Iteratively merge all overlapping or adjacent rectangles into the smallest set.

    Args:
        rects (list): A list of pygame.Rect objects.

    Returns:
        list: A list of merged pygame.Rect objects.
    """
    merged = True
    while merged:
        merged = False
        new_rects = []
        used = [False] * len(rects)

        for i, current in enumerate(rects):
            if used[i]:
                continue
            to_merge = [current]

            for j, other in enumerate(rects):
                if i != j and not used[j] and (
                    current.colliderect(other) or are_adjacent(current, other)
                ):
                    to_merge.append(other)
                    used[j] = True

            # Merge all rects in `to_merge` into one
            merged_rect = merge_rects(to_merge)
            new_rects.append(merged_rect)

        if len(new_rects) < len(rects):
            merged = True

        rects = new_rects

    return rects

def are_adjacent(rect1, rect2):
    """
    Check if two pygame.Rect objects are adjacent (share an edge).

    Args:
        rect1 (pygame.Rect): The first rectangle.
        rect2 (pygame.Rect): The second rectangle.

    Returns:
        bool: True if the rectangles are adjacent, False otherwise.
    """
    # Check horizontal adjacency
    if rect1.right == rect2.left or rect1.left == rect2.right:
        if rect1.top < rect2.bottom and rect1.bottom > rect2.top:
            return True

    # Check vertical adjacency
    if rect1.bottom == rect2.top or rect1.top == rect2.bottom:
        if rect1.left < rect2.right and rect1.right > rect2.left:
            return True

    return False

def merge_rects(rects):
    """
    Merge a list of pygame.Rect objects into a single rectangle.

    Args:
        rects (list): A list of pygame.Rect objects.

    Returns:
        pygame.Rect: A single merged rectangle.
    """
    x_min = min(r.x for r in rects)
    y_min = min(r.y for r in rects)
    x_max = max(r.right for r in rects)
    y_max = max(r.bottom for r in rects)

    return pygame.Rect(x_min, y_min, x_max - x_min, y_max - y_min)


def load_image(path,res):
    r = res if isinstance(res,tuple) else (res,res)
    try:
        return pygame.transform.scale(pygame.image.load(path),r)
    except FileNotFoundError:
        return pygame.transform.scale(pygame.image.load("assets/error.png"),r)
    
import heapq

class Node:
    def __init__(self, position, g, h, parent=None):
        self.position = position  # (x, y)
        self.g = g  # Cost from start to current node
        self.h = h  # Heuristic cost to goal
        self.f = g + h  # Total cost
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def pathfind(start, goal, obstacles=[]):
    """
    A* pathfinding algorithm to find the shortest path from start to goal.

    Args:
        start (tuple): Starting position (x, y).
        goal (tuple): Goal position (x, y).
        obstacles (list): List of pygame.Rect objects representing obstacles.

    Returns:
        list: A simplified list of (x, y) tuples representing the path.
    """
    open_list = []
    heapq.heappush(open_list, Node(start, g=0, h=heuristic(start, goal)))
    closed_set = set()
    came_from = {}

    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_list:
        current = heapq.heappop(open_list).position

        if current == goal:
            path = reconstruct_path(came_from, current)
            return simplify_path(path)

        closed_set.add(current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if neighbor in closed_set or not valid(neighbor, obstacles):
                continue

            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_list, Node(neighbor, g=g_score[neighbor], h=heuristic(neighbor, goal)))

    return None  # No path found


def reconstruct_path(came_from, current):
    """
    Reconstruct the path from the came_from map.

    Args:
        came_from (dict): Map of nodes to their predecessors.
        current (tuple): Current position.

    Returns:
        list: A list of (x, y) tuples representing the path.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def simplify_path(path):
    """
    Simplify the path by removing intermediate points on the same straight line
    and converting it into direction tuples.

    Args:
        path (list): A list of (x, y) tuples representing the path.

    Returns:
        list: A simplified list of direction tuples (dx, dy).
    """
    if len(path) <= 1:
        return []

    directions = []
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        direction = (dx // max(1, abs(dx)), dy // max(1, abs(dy)))  # Normalize to unit direction
        directions.append(direction)

    return directions


def valid(pos, obstacles):
    """
    Check if a position is valid (not colliding with any obstacles).

    Args:
        pos (tuple): Position to check (x, y).
        obstacles (list): List of pygame.Rect objects representing obstacles.

    Returns:
        bool: True if the position is valid, False otherwise.
    """
    point_rect = pygame.Rect(pos[0], pos[1], 1, 1)
    return not any(point_rect.colliderect(obstacle) for obstacle in obstacles)




