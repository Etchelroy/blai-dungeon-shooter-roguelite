import pygame, math
from constants import SCREEN_W, SCREEN_H, BLACK

class LightSource:
    def __init__(self, x, y, radius, color, intensity=1.0, flicker=False):
        self.x=x; self.y=y; self.radius=radius
        self.color=color; self.intensity=intensity
        self.flicker=flicker
        self._flicker_t=0

    def update(self, dt):
        if self.flicker:
            import random
            self._flicker_t += dt
            self.intensity = 0.8 + 0.2*math.sin(self._flicker_t*8) + random.uniform(-0.05,0.05)

class LightingSystem:
    def __init__(self):
        self.sources = []
        self._surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self.ambient = 60

    def add(self, source):
        self.sources.append(source)

    def remove(self, source):
        if source in self.sources:
            self.sources.remove(source)

    def clear(self):
        self.sources.clear()

    def update(self, dt):
        for s in self.sources:
            s.update(dt)

    def render(self, surf, camera):
        self._surf.fill((0, 0, 0, 255 - self.ambient))
        for src in self.sources:
            sx, sy = camera.apply(src.x, src.y)
            r = int(src.radius * src.intensity)
            if r <= 0:
                continue
            r = min(r, 600)
            light = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            for ring in range(r, 0, -max(1,r//20)):
                alpha = int(255 * (1 - ring/r) * src.intensity)
                alpha = max(0, min(255, alpha))
                c = (*src.color[:3], alpha)
                pygame.draw.circle(light, c, (r,r), ring)
            # Use BLEND_RGBA_SUB to subtract darkness
            self._surf.blit(light, (sx-r, sy-r), special_flags=pygame.BLEND_RGBA_SUB)
        surf.blit(self._surf, (0,0))