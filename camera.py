import pygame
from constants import *
from utils import lerp, clamp

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.shake_intensity = 0.0
        self.shake_timer = 0.0
        self.ox = 0
        self.oy = 0

    def update(self, target_x, target_y, dt, map_pixel_w, map_pixel_h):
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2
        self.x = lerp(self.x, self.target_x, min(1.0, dt * 8))
        self.y = lerp(self.y, self.target_y, min(1.0, dt * 8))
        max_x = max(0, map_pixel_w - SCREEN_WIDTH)
        max_y = max(0, map_pixel_h - SCREEN_HEIGHT)
        self.x = clamp(self.x, 0, max_x)
        self.y = clamp(self.y, 0, max_y)
        self.ox = 0
        self.oy = 0
        if self.shake_timer > 0:
            self.shake_timer -= dt
            import random
            si = self.shake_intensity * (self.shake_timer / max(0.01, self.shake_timer + dt))
            self.ox = random.randint(-int(si), int(si))
            self.oy = random.randint(-int(si), int(si))

    def shake(self, intensity=8, duration=0.3):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)

    def world_to_screen(self, wx, wy):
        return (wx - self.x + self.ox, wy - self.y + self.oy)

    def screen_to_world(self, sx, sy):
        return (sx + self.x - self.ox, sy + self.y - self.oy)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), SCREEN_WIDTH, SCREEN_HEIGHT)