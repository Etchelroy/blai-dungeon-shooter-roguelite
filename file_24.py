import pygame
import math
from settings import *

class LightSource:
    def __init__(self, x, y, radius, color, intensity=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = 0.0

class LightingSystem:
    def __init__(self, arena_w, arena_h):
        self.arena_w = arena_w
        self.arena_h = arena_h
        self.sources = []
        self.ambient = AMBIENT_LIGHT
        self._surf = None
        self._last_size = None

    def update(self, dt, player, enemies):
        self.sources.clear()
        self.sources.append(LightSource(player.x, player.y, LIGHT_RADIUS, (255,220,180), 1.0))
        for e in enemies:
            if hasattr(e, 'light_color'):
                self.sources.append(LightSource(e.x, e.y, 120, e.light_color, 0.6))

    def render(self, camera):
        w, h = camera.sw, camera.sh
        if self._last_size != (w, h):
            self._surf = pygame.Surface((w, h), pygame.SRCALPHA)
            self._last_size = (w, h)
        surf = self._surf
        surf.fill((self.ambient, self.ambient, self.ambient, 255))
        for src in self.sources:
            sx