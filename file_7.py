from src.utils import lerp, clamp

class Camera:
    def __init__(self, vw, vh, aw, ah):
        self.vw = vw; self.vh = vh
        self.aw = aw; self.ah = ah
        self.x = 0.0; self.y = 0.0
        self.shake_x = 0; self.shake_y = 0
        self._shake_timer = 0
        self._shake_intensity = 0
        import random
        self._rand = random.Random()

    def update(self, target_x, target_y, dt):
        tx = target_x - self.vw/2
        ty = target_y - self.vh/2
        tx = clamp(tx, 0, self.aw - self.vw)
        ty = clamp(ty, 0, self.ah - self.vh)
        self.x = lerp(self.x, tx, min(1.0, dt*8))
        self.y = lerp(self.y, ty, min(1.0, dt*8))
        if self._shake_timer > 0:
            self._shake_timer -= dt
            i = self._shake_intensity * (self._shake_timer / max(self._shake_timer+dt,0.001))
            self.shake_x = self._rand.randint(-int(i), int(i))
            self.shake_y = self._rand.randint(-int(i), int(i))
        else:
            self.shake_x = 0; self.shake_y = 0

    def shake(self, intensity=8, duration=0.3):
        self._shake_intensity = intensity
        self._shake_timer = duration

    @property
    def ox(self):
        return int(self.x) + self.shake_x

    @property
    def oy(self):
        return int(self.y) + self.shake_y

    def world_to_screen(self, wx, wy):
        return wx - self.ox, wy - self.oy

    def screen_to_world(self, sx, sy):
        return sx + self.ox, sy + self.oy