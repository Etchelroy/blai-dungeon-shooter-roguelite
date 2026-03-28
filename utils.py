import pygame
import math
import random

def vec2_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1])

def vec2_norm(v):
    l = vec2_len(v)
    if l == 0:
        return (0.0, 0.0)
    return (v[0]/l, v[1]/l)

def vec2_add(a, b):
    return (a[0]+b[0], a[1]+b[1])

def vec2_sub(a, b):
    return (a[0]-b[0], a[1]-b[1])

def vec2_scale(v, s):
    return (v[0]*s, v[1]*s)

def vec2_dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def vec2_dist(a, b):
    return vec2_len(vec2_sub(b, a))

def angle_to(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    return math.atan2(dy, dx)

def dir_from_angle(angle):
    return (math.cos(angle), math.sin(angle))

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0, 1)

def rand_color_variation(base, amt=30):
    r = clamp(base[0] + random.randint(-amt, amt), 0, 255)
    g = clamp(base[1] + random.randint(-amt, amt), 0, 255)
    b = clamp(base[2] + random.randint(-amt, amt), 0, 255)
    return (r, g, b)

def draw_bar(surface, x, y, w, h, val, max_val, fg_color, bg_color=(30,30,30), border=1):
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    fill = int(w * clamp(val/max(max_val,1), 0, 1))
    if fill > 0:
        pygame.draw.rect(surface, fg_color, (x, y, fill, h))
    if border:
        pygame.draw.rect(surface, (200,200,200), (x, y, w, h), border)

def rot_center(image, angle, pos):
    rotated = pygame.transform.rotate(image, -math.degrees(angle))
    rect = rotated.get_rect(center=pos)
    return rotated, rect

def screen_shake_offset(intensity, decay):
    if intensity <= 0:
        return (0, 0)
    x = random.uniform(-intensity, intensity)
    y = random.uniform(-intensity, intensity)
    return (x, y)

def point_in_rect(pt, rect):
    return rect[0] <= pt[0] <= rect[0]+rect[2] and rect[1] <= pt[1] <= rect[1]+rect[3]

def circles_overlap(ax, ay, ar, bx, by, br):
    dx = ax - bx
    dy = ay - by
    return (dx*dx + dy*dy) < (ar+br)*(ar+br)

def random_point_in_ring(cx, cy, rmin, rmax):
    angle = random.uniform(0, math.pi*2)
    r = random.uniform(rmin, rmax)
    return (cx + math.cos(angle)*r, cy + math.sin(angle)*r)