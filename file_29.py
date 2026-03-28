from utils import lerp, clamp
from settings import SCREEN_W, SCREEN_H, ARENA_W, ARENA_H

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self._shake_x = 0.0
        self._shake_y = 0.0

    def set_target(self, cx, cy):
        self.target_x = cx - SCREEN_W // 2
        self.target_y = cy - SCREEN_H // 2

    def update(self, dt):
        import random
        self.x = lerp(self.x, self.target_x, min(1.0, 8.0 * dt))
        self.y = lerp(self.y, self.target_y, min(1.0, 8.0 * dt))
        self.x = clamp(self.x, 0, ARENA_W - SCREEN_W)
        self.y = clamp(self.y, 0, ARENA_H - SCREEN_H)
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self._shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self._shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self._shake_x = 0.0
            self._shake_y = 0.0

    def shake(self, intensity, duration):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    @property
    def ox(self):
        return self.x + self._shake_x

    @property
    def oy(self):
        return self.y + self._shake_y

    def world_to_screen(self, wx, wy):
        return wx - self.ox, wy - self.oy

    def screen_to_world(self, sx, sy):
        return sx + self.ox, sy + self.oy