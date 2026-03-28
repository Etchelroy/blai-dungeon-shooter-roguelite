from utils import lerp, clamp

class Camera:
    def __init__(self, sw, sh, world_w, world_h):
        self.sw = sw
        self.sh = sh
        self.world_w = world_w
        self.world_h = world_h
        self.x = 0.0
        self.y = 0.0
        self.shake = 0.0
        self.shake_dx = 0.0
        self.shake_dy = 0.0
        import random
        self._rng = random

    def follow(self, tx, ty, dt):
        target_x = tx - self.sw / 2
        target_y = ty - self.sh / 2
        self.x = lerp(self.x, target_x, min(1.0, 8 * dt))
        self.y = lerp(self.y, target_y, min(1.0, 8 * dt))
        self.x = clamp(self.x, 0, max(0, self.world_w - self.sw))
        self.y = clamp(self.y, 0, max(0, self.world_h - self.sh))
        if self.shake > 0:
            self.shake_dx = self._rng.uniform(-self.shake, self.shake)
            self.shake_dy = self._rng.uniform(-self.shake, self.shake)
            self.shake = max(0, self.shake - 120 * dt)
        else:
            self.shake_dx = 0
            self.shake_dy = 0

    def add_shake(self, amount):
        self.shake = min(self.shake + amount, 18)

    def world_to_screen(self, wx, wy):
        return (wx - self.x + self.shake_dx, wy - self.y + self.shake_dy)

    def screen_to_world(self, sx, sy):
        return (sx + self.x - self.shake_dx, sy + self.y - self.shake_dy)

    def in_view(self, x, y, margin=64):
        sx, sy = self.world_to_screen(x, y)
        return -margin <= sx <= self.sw+margin and -margin <= sy <= self.sh+margin