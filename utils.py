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
