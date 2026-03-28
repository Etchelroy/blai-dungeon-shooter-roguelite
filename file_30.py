import pygame
import math
from constants import SCREEN_W, SCREEN_H

class Light:
    def __init__(self, x, y, radius, color, intensity=1.0, flicker=False):
        self.x = x; self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = flicker
        self._flicker_t = 0.0

    def update(self, dt):
        if self.flicker:
            import random
            self._flicker_t += dt * 8
            self.intensity = 0.8 + 0.2 * math.sin(self._flicker_t) + random.uniform(-0.05, 0.05)

class LightingSystem:
    def __init__(self):
        self.lights = []
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def clear_lights(self):
        self.lights.clear()

    def add_light(self, x, y, radius, color=(255,220,150), intensity=1.0, flicker=False):
        self.lights.append(Light(x, y, radius, color, intensity, flicker))

    def update(self, dt):
        for l in self.lights:
            l.update(dt)

    def render(self, surface, cam):
        self._overlay.fill((0, 0, 0, 160))
        for light in self.lights:
            sx, sy = cam.apply(light.x, light.y)
            r = int(light.radius * light.intensity)
            if r <= 0:
                continue
            if sx + r < 0 or sx - r > SCREEN_W or sy + r < 0 or sy - r > SCREEN_H:
                continue
            ls = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            cr, cg, cb = light.color[:3]
            for step in range(8, 0, -1):
                frac = step / 8
                alpha = int(120 * (1 - frac) * light.intensity)
                rad = int(r * frac)
                pygame.draw.circle(ls, (cr, cg, cb, alpha), (r, r), rad)
            self._overlay.blit(ls, (sx - r, sy - r), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(self._overlay, (0, 0))