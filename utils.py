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
    
# Optimized pathfinding utilities - replace the pathfinding section in utils.py

import heapq
import pygame
import math

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
    # Manhattan distance for faster computation
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def pathfind(start, goal, obstacles=[], grid_size=16, max_iterations=500):
    """
    Optimized A* pathfinding algorithm with grid-based movement and early termination.
    
    Args:
        start (tuple): Starting position (x, y).
        goal (tuple): Goal position (x, y).
        obstacles (list): List of pygame.Rect objects representing obstacles.
        grid_size (int): Size of each grid cell for pathfinding (larger = faster but less precise)
        max_iterations (int): Maximum iterations before giving up
    
    Returns:
        list: A simplified list of (dx, dy) direction tuples representing the path.
    """
    # Convert positions to grid coordinates
    start_grid = (start[0] // grid_size, start[1] // grid_size)
    goal_grid = (goal[0] // grid_size, goal[1] // grid_size)
    
    # Early exit if start and goal are the same
    if start_grid == goal_grid:
        return [(0, 0)]
    
    # Early exit if goal is too far (optional performance check)
    distance = heuristic(start_grid, goal_grid)
    if distance > 100:  # Adjust this threshold as needed
        # Return direct path if too far
        dx = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
        dy = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0
        return [(dx, dy)]
    
    # Create obstacle grid for faster collision detection
    obstacle_grid = create_obstacle_grid(obstacles, grid_size)
    
    open_list = []
    heapq.heappush(open_list, Node(start_grid, g=0, h=heuristic(start_grid, goal_grid)))
    closed_set = set()
    came_from = {}
    
    g_score = {start_grid: 0}
    iterations = 0
    
    # 8-directional movement (including diagonals)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    while open_list and iterations < max_iterations:
        iterations += 1
        current = heapq.heappop(open_list).position
        
        if current == goal_grid:
            path = reconstruct_path(came_from, current)
            return simplify_path_optimized(path, start, goal, grid_size)
        
        closed_set.add(current)
        
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if neighbor in closed_set:
                continue
                
            # Check if neighbor is valid using pre-computed obstacle grid
            if not is_valid_grid_position(neighbor, obstacle_grid, grid_size):
                continue
            
            # Calculate movement cost (diagonal movement costs more)
            move_cost = 1.4 if dx != 0 and dy != 0 else 1.0
            tentative_g_score = g_score[current] + move_cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal_grid)
                heapq.heappush(open_list, Node(neighbor, g=g_score[neighbor], h=heuristic(neighbor, goal_grid)))
    
    # Fallback: return direct movement if no path found
    dx = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
    dy = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0
    return [(dx, dy)]

def create_obstacle_grid(obstacles, grid_size):
    """
    Create a set of grid positions that contain obstacles for faster lookup.
    """
    obstacle_grid = set()
    
    for obstacle in obstacles:
        # Get grid bounds for this obstacle
        left = obstacle.left // grid_size
        right = (obstacle.right - 1) // grid_size + 1
        top = obstacle.top // grid_size
        bottom = (obstacle.bottom - 1) // grid_size + 1
        
        # Mark all grid cells that intersect with this obstacle
        for x in range(left, right):
            for y in range(top, bottom):
                obstacle_grid.add((x, y))
    
    return obstacle_grid

def is_valid_grid_position(pos, obstacle_grid, grid_size):
    """
    Check if a grid position is valid (not blocked by obstacles).
    """
    return pos not in obstacle_grid

def reconstruct_path(came_from, current):
    """
    Reconstruct the path from the came_from map.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def simplify_path_optimized(path, start, goal, grid_size):
    """
    Convert grid path to world directions and simplify.
    """
    if len(path) <= 1:
        # Fallback to direct movement
        dx = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
        dy = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0
        return [(dx, dy)]
    
    # Convert first step from grid to world direction
    grid_dx = path[1][0] - path[0][0]
    grid_dy = path[1][1] - path[0][1]
    
    # Normalize to unit direction
    dx = max(-1, min(1, grid_dx))
    dy = max(-1, min(1, grid_dy))
    
    return [(dx, dy)]

# Fast line-of-sight check for simple cases
def has_line_of_sight(start, goal, obstacles, step_size=16):
    """
    Quick check if there's a direct line of sight between two points.
    """
    dx = goal[0] - start[0]
    dy = goal[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance == 0:
        return True
    
    steps = int(distance // step_size) + 1
    step_x = dx / steps
    step_y = dy / steps
    
    for i in range(1, steps):
        test_x = start[0] + step_x * i
        test_y = start[1] + step_y * i
        test_rect = pygame.Rect(test_x - 8, test_y - 8, 16, 16)
        
        for obstacle in obstacles:
            if test_rect.colliderect(obstacle):
                return False
    
    return True

# Enhanced pathfinding function that tries line of sight first
def smart_pathfind(start, goal, obstacles, grid_size=16):
    """
    Smart pathfinding that tries direct movement first, then falls back to A*.
    """
    # First, check if we have direct line of sight
    if has_line_of_sight(start, goal, obstacles):
        dx = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
        dy = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0
        return [(dx, dy)]
    
    # Otherwise, use A* pathfinding
    return pathfind(start, goal, obstacles, grid_size)