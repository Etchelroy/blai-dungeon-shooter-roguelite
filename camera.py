import pygame, random, math
from constants import SCREEN_W, SCREEN_H, TILE, ARENA_W, ARENA_H

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake_intensity = 0.0
        self.shake_timer = 0.0
        self.ox = 0.0
        self.oy = 0.0

    def update(self, target_x, target_y, dt):
        tx = target_x - SCREEN_W//2
        ty = target_y - SCREEN_H//2
        max_x = ARENA_W * TILE - SCREEN_W
        max_y = ARENA_H * TILE - SCREEN_H
        tx = max(0, min(tx, max_x)) if max_x > 0 else 0
        ty = max(0, min(ty, max_y)) if max_y > 0 else 0
        self.x += (tx - self.x) * min(1.0, dt*8)
        self.y += (ty - self.y) * min(1.0, dt*8)
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.ox = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.oy = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.ox = 0; self.oy = 0

    def shake(self, intensity=8, duration=0.3):
        self.shake_intensity = intensity
        self.shake_timer = duration

    def apply(self, x, y):
        return x - self.x + self.ox, y - self.y + self.oy

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.x + self.ox, rect.y - self.y + self.oy, rect.width, rect.height)

    def world_to_screen(self, x, y):
        return x - self.x + self.ox, y - self.y + self.oy

    def screen_to_world(self, sx, sy):
        return sx + self.x - self.ox, sy + self.y - self.oy