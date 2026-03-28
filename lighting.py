import pygame
import math
from constants import *

class LightSource:
    def __init__(self, x, y, radius, color=(255,220,150), intensity=1.0, flicker=False):
        self.x = x; self.y = y; self.radius = radius
        self.color = color; self.intensity = intensity
        self.flicker = flicker
        self._phase = 0.0

    def update(self, dt):
        if self.flicker:
            import random
            self._phase += dt * 8
            self.intensity = 0.85 + 0.15 * math.sin(self._phase) + random.uniform(-0.05, 0.05)

class LightingSystem:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.darkness = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self.sources = []
        self.ambient = 60

    def clear(self):
        self.sources = []

    def add(self, source):
        self.sources.append(source)

    def add_light(self, x, y, radius, color=(255,220,150), intensity=1.0, flicker=False):
        self.sources.append(LightSource(x, y, radius, color, intensity, flicker))

    def update(self, dt):
        for s in self.sources:
            s.update(dt)

    def render(self, surface, camera):
        self.darkness.fill((0, 0, 0, max(0, 220 - self.ambient)))
        for src in self.sources:
            sx, sy = camera.world_to_screen(src.x, src.y)
            r = int(src.radius * src.intensity)
            if r <= 0:
                continue
            if sx + r < 0 or sx - r > self.w or sy + r < 0 or sy - r > self.h:
                continue
            light_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            for ring in range(5):
                ring_r = int(r * (1 - ring/5))
                alpha = int(180 * (ring/5))
                c = (*src.color, alpha)
                pygame.draw.circle(light_surf, c, (r, r), ring_r)
            self.darkness.blit(light_surf, (int(sx)-r, int(sy)-r), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(self.darkness, (0, 0))