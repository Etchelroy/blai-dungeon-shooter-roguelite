import math
import pygame
import random

def normalize(v):
    x, y = v
    mag = math.hypot(x, y)
    if mag == 0:
        return (0, 0)
    return (x / mag, y / mag)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def angle_to(src, dst):
    return math.atan2(dst[1] - src[1], dst[0] - src[0])

def vec_from_angle(angle, mag=1.0):
    return (math.cos(angle) * mag, math.sin(angle) * mag)

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def lerp(a, b, t):
    return a + (b - a) * t

def rand_color_variation(base, amount=30):
    r, g, b = base
    return (
        clamp(r + random.randint(-amount, amount), 0, 255),
        clamp(g + random.randint(-amount, amount), 0, 255),
        clamp(b + random.randint(-amount, amount), 0, 255)
    )

def draw_bar(surface, x, y, w, h, val, max_val, fg, bg=(40,40,40), border=(0,0,0)):
    pygame.draw.rect(surface, bg, (x, y, w, h))
    fill = int(w * clamp(val / max(max_val, 1), 0, 1))
    if fill > 0:
        pygame.draw.rect(surface, fg, (x, y, fill, h))
    pygame.draw.rect(surface, border, (x, y, w, h), 1)

def rot_center(image, angle, pos):
    rotated = pygame.transform.rotate(image, -math.degrees(angle))
    rect = rotated.get_rect(center=pos)
    return rotated, rect

def screen_shake_offset(intensity, duration_left):
    if duration_left <= 0:
        return (0, 0)
    mag = intensity * (duration_left / 0.3)
    return (random.uniform(-mag, mag), random.uniform(-mag, mag))