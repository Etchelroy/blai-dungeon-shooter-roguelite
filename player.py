import pygame
import math
import random
from settings import *
from weapons import Weapon, Projectile
from abilities import create_ability

PLAYER_SPEED = 220.0
DASH_SPEED = 600.0
DASH_DURATION = 0.15
DASH_COOLDOWN = 0.8
MELEE_COOLDOWN = 0.5
MELEE_DAMAGE = 35
MELEE_RANGE = 70

class Afterimage:
    def __init__(self, x, y, angle, alpha=180):
        self.x = x
        self.y = y
        self.angle = angle
        self.alpha = alpha
        self.lifetime = 0.2

    def update(self, dt):
        self.lifetime -= dt
        self.alpha = int(180 * (self.lifetime / 0.2))

    def render(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        draw_player_sprite(s, 16, 16, 0, alpha=self.alpha, color=(100, 180, 255))
        screen.blit(s, (int(sx) - 16, int(sy) - 16))


def draw_player_sprite(surf, cx, cy, angle, alpha=255, color=(80, 160, 240)):
    body_color = color
    dark = tuple(max(0, c - 40) for c in color)
    # Body
    pygame.draw.ellipse(surf, body_color, (cx - 10, cy - 12, 20, 22))
    pygame.draw.ellipse(surf, dark, (cx - 10, cy - 12, 20, 22), 2)
    # Head
    pygame.draw.circle(surf, (220, 190, 150), (cx, cy - 10), 7)
    # Gun direction indicator
    gx = cx + math.cos(angle) * 14
    gy = cy + math.sin(angle) * 14
    pygame.draw.line(surf, (200, 200, 200), (cx, cy), (int(gx), int(gy)), 3)
    pygame.draw.circle(surf, (160, 160, 180), (int(gx), int(gy)), 3)