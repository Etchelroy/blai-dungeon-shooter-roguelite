import pygame
import math
import random

def normalize(vec):
    length = math.hypot(vec[0], vec[1])
    if length == 0:
        return (0.0, 0.0)
    return (vec[0] / length, vec[1] / length)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def angle_to(src, dst):
    return math.atan2(dst[1] - src[1], dst[0] - src[0])

def vec_from_angle(angle, speed=1.0):
    return (math.cos(angle) * speed, math.sin(angle) * speed)

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def lerp(a, b, t):
    return a + (b - a) * t

def rand_color_variation(base_color, variation=30):
    r = clamp(base_color[0] + random.randint(-variation, variation), 0, 255)
    g = clamp(base_color[1] + random.randint(-variation, variation), 0, 255)
    b = clamp(base_color[2] + random.randint(-variation, variation), 0, 255)
    return (r, g, b)

def draw_bar(surface, x, y, w, h, value, max_value, fg_color, bg_color=(40,40,40), border=2):
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    if max_value > 0:
        filled = int(w * clamp(value / max_value, 0, 1))
        if filled > 0:
            pygame.draw.rect(surface, fg_color, (x, y, filled, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), border)

def screen_shake_offset(intensity, duration_left):
    if duration_left <= 0:
        return (0, 0)
    ox = random.randint(-int(intensity), int(intensity))
    oy = random.randint(-int(intensity), int(intensity))
    return (ox, oy)

def point_in_rect(point, rect):
    return rect.collidepoint(point)

def circles_overlap(ax, ay, ar, bx, by, br):
    return math.hypot(ax - bx, ay - by) < (ar + br)

def rot_surface(surface, angle):
    return pygame.transform.rotate(surface, -math.degrees(angle))

def make_surface(w, h, color, alpha=255):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((*color[:3], alpha))
    return surf