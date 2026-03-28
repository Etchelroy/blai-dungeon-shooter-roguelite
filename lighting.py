import pygame
from constants import SCREEN_W, SCREEN_H
from utils import clamp

class LightSource:
    def __init__(self, x, y, radius, color=(255,220,150), intensity=1.0):
        self.x = x; self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = 0.0

class LightingSystem:
    def __init__(self):
        self.lights = []
        self.ambient = 60
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def clear(self):
        self.lights = []

    def add(self, x, y, radius, color=(255,220,150), intensity=1.0):
        self.lights.append(LightSource(x, y, radius, color, intensity))

    def update(self, dt):
        import random
        for l in self.lights:
            if l.flicker:
                l.intensity = clamp(l.intensity + random.uniform(-0.05,0.05), 0.6, 1.0)

    def draw(self, surface, cam_offset):
        ox, oy = cam_offset
        overlay = self._overlay
        overlay.fill((0, 0, 0, max(0, 220 - self.ambient)))
        for l in self.lights:
            sx = int(l.x - ox)
            sy = int(l.y - oy)
            r = int(l.radius * l.intensity)
            if r <= 0:
                continue
            light_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            for ring in range(r, 0, -max(1, r//8)):
                alpha = int(180 * (1 - ring/r) * l.intensity)
                col = (l.color[0], l.color[1], l.color[2], clamp(alpha, 0, 180))
                pygame.draw.circle(light_surf, col, (r, r), ring)
            overlay.blit(light_surf, (sx-r, sy-r), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(overlay, (0, 0))