import pygame
import math
import random

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def normalize(dx, dy):
    mag = math.sqrt(dx*dx + dy*dy)
    if mag == 0:
        return 0.0, 0.0
    return dx/mag, dy/mag

def angle_to(x1, y1, x2, y2):
    return math.atan2(y2-y1, x2-x1)

def draw_pixel_rect(surf, color, x, y, w, h, border=0, border_color=None):
    pygame.draw.rect(surf, color, (x, y, w, h))
    if border and border_color:
        pygame.draw.rect(surf, border_color, (x, y, w, h), border)

def draw_health_bar(surf, x, y, w, h, val, maxv, color=(60,220,60), bg=(60,20,20)):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    fill = int(w * clamp(val/maxv, 0, 1))
    if fill > 0:
        pygame.draw.rect(surf, color, (x, y, fill, h))
    pygame.draw.rect(surf, (200,200,200), (x, y, w, h), 1)

def make_surface(w, h, color=None, alpha=True):
    flags = pygame.SRCALPHA if alpha else 0
    s = pygame.Surface((w, h), flags)
    if color:
        s.fill(color)
    return s

def random_color():
    return (random.randint(80,255), random.randint(80,255), random.randint(80,255))