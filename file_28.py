import pygame
from constants import SCREEN_W, SCREEN_H
import utils

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake_intensity = 0.0
        self.shake_timer = 0.0
        self._ox = 0
        self._oy = 0

    def update(self, target_x, target_y, dt):
        cx = target_x - SCREEN_W / 2
        cy = target_y - SCREEN_H / 2
        self.x += (cx - self.x) * min(1.0, 8 * dt)
        self.y += (cy - self.y) * min(1.0, 8 * dt)
        if self.shake_timer > 0:
            self.shake_timer -= dt
            ox, oy = utils.screen_shake_offset(self.shake_intensity, self.shake_timer)
        else:
            ox, oy = 0, 0
        self._ox = int(ox)
        self._oy = int(oy)

    def shake(self, intensity=8.0, duration=0.3):
        self.shake_intensity = intensity
        self.shake_timer = duration

    def apply(self, x, y):
        return (int(x - self.x) + self._ox, int(y - self.y) + self._oy)

    def apply_rect(self, rect):
        return pygame.Rect(
            rect.x - int(self.x) + self._ox,
            rect.y - int(self.y) + self._oy,
            rect.width, rect.height
        )

    def world_to_screen(self, x, y):
        return self.apply(x, y)

    def screen_to_world(self, sx, sy):
        return (sx + self.x - self._ox, sy + self.y - self._oy)