import math
import pygame
import random

def normalize(vx, vy):
    mag = math.hypot(vx, vy)
    if mag == 0:
        return 0.0, 0.0
    return vx / mag, vy / mag

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def angle_to(ax, ay, bx, by):
    return math.atan2(by - ay, bx - ax)

def vec_from_angle(angle):
    return math.cos(angle), math.sin(angle)

def rand_color_var(base, var=20):
    return tuple(clamp(c + random.randint(-var, var), 0, 255) for c in base)

def draw_rect_alpha(surface, color, rect, alpha):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    s.fill((*color[:3], alpha))
    surface.blit(s, (rect[0], rect[1]))

def rotate_surface(surf, angle_deg):
    return pygame.transform.rotate(surf, -angle_deg)

def scale_surface(surf, scale):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (int(w * scale), int(h * scale)))

def typewriter(font, text, progress, color=(255,255,255)):
    n = int(len(text) * progress)
    return font.render(text[:n], True, color)

class Timer:
    def __init__(self, duration, repeat=False):
        self.duration = duration
        self.repeat = repeat
        self.elapsed = 0.0
        self.done = False

    def update(self, dt):
        if self.done and not self.repeat:
            return
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.done = True
            if self.repeat:
                self.elapsed %= self.duration

    def reset(self):
        self.elapsed = 0.0
        self.done = False

    @property
    def progress(self):
        return clamp(self.elapsed / self.duration, 0.0, 1.0)