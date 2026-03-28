import pygame
import math
from settings import SCREEN_W, SCREEN_H

class LightSource:
    def __init__(self, x, y, radius, color=(255,220,150), intensity=1.0, flicker=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = flicker
        self._t = 0.0

    def update(self, dt):
        if self.flicker:
            self._t += dt
            self.intensity = 0.85 + 0.15 * math.sin(self._t * 8 + math.sin(self._t * 13))

class LightingSystem:
    def __init__(self):
        self.lights = []
        self.ambient = 40
        self._surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def clear(self):
        self.lights.clear()

    def add(self, light):
        self.lights.append(light)

    def update(self, dt):
        for l in self.lights:
            l.update(dt)

    def render(self, screen, cam_ox, cam_oy):
        self._surf.fill((0, 0, 0, 255 - self.ambient))
        for light in self.lights:
            sx = int(light.x - cam_ox)
            sy = int(light.y - cam_oy)
            r = int(light.radius * light.intensity)
            if sx + r < 0 or sx - r > SCREEN_W or sy + r < 0 or sy - r > SCREEN_H:
                continue
            for ring in range(r, 0, -max(1, r//12)):
                frac = ring / r
                a = int((1.0 - frac) * 200 * light.intensity)
                c = (*light.color, a)
                pygame.draw.circle(self._surf, c, (sx, sy), ring)
        screen.blit(self._surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)