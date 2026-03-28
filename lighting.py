import pygame
import math
from settings import *

class LightSource:
    def __init__(self, x, y, radius, color, intensity=1.0, flicker=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = flicker
        self.flicker_offset = 0.0
        self.time = 0.0

    def update(self, dt):
        if self.flicker:
            self.time += dt
            import math
            self.flicker_offset = math.sin(self.time * 8.0) * 0.15

    def get_intensity(self):
        return max(0.0, min(1.0, self.intensity + self.flicker_offset))


class LightingSystem:
    def __init__(self):
        self.lights = []
        self.ambient = 0.18
        self.surface = pygame.Surface((VIEWPORT_W, VIEWPORT_H), pygame.SRCALPHA)
        self.enabled = True

    def add_light(self, light):
        self.lights.append(light)
        return light

    def remove_light(self, light):
        if light in self.lights:
            self.lights.remove(light)

    def clear(self):
        self.lights.clear()

    def update(self, dt):
        for l in self.lights:
            l.update(dt)

    def render(self, screen, camera):
        if not self.enabled:
            return
        self.surface.fill((0, 0, 0, int((1.0 - self.ambient) * 220)))
        for light in self.lights:
            sx, sy = camera.world_to_screen(light.x, light.y)
            r = light.radius
            if sx + r < 0 or sx - r > VIEWPORT_W or sy + r < 0 or sy - r > VIEWPORT_H:
                continue
            inten = light.get_intensity()
            light_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            c = light.color
            for ring in range(int(r), 0, -max(1, int(r // 20))):
                alpha = int(inten * 180 * (1.0 - ring / r) ** 1.5)
                alpha = max(0, min(255, alpha))
                pygame.draw.circle(light_surf, (c[0], c[1], c[2], alpha), (r, r), ring)
            self.surface.blit(light_surf, (sx - r, sy - r), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(self.surface, (0, 0))