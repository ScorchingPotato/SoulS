import pygame

def create_soft_light(radius, color=(255, 255, 255)):
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        # Cubic falloff for a more cartoony effect
        alpha = int(255 * (r / radius) ** 3)
        # Add a slight color gradient by modifying the RGB values
        gradient_color = (
            min(255, color[0] + int(50 * (1 - r / radius))),
            min(255, color[1] + int(50 * (1 - r / radius))),
            min(255, color[2] + int(50 * (1 - r / radius))),
        )
        pygame.draw.circle(surface, (*gradient_color, alpha), (radius, radius), r)
    return surface


def load_image(path,res):
    r = res if isinstance(res,tuple) else (res,res)
    try:
        return pygame.transform.scale(pygame.image.load(path),r)
    except FileNotFoundError:
        return pygame.transform.scale(pygame.image.load("assets/error.png"),r)
