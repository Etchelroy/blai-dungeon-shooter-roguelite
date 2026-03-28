import pygame
import math
import random
from utils import lerp, color_lerp

MAX_PARTICLES = 2000

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','end_color',
                 'size','end_size','gravity','active','ptype','angle','spin']
    def __init__(self):
        self.active = False

class ParticleSystem:
    def __init__(self):
        self.pool = [Particle() for _ in range(MAX_PARTICLES)]
        self.active_list = []

    def clear(self):
        for p in self.pool:
            p.active = False
        self.active_list.clear()

    def _get_free(self):
        for p in self.pool:
            if not p.active:
                return p
        return None

    def emit(self, x, y, vx, vy, life, color, end_color=None, size=4, end_size=0,
             gravity=0, ptype='circle', count=1, spread=0, spin=0):
        for _ in range(count):
            p = self._get_free()
            if p is None:
                break
            p.active = True
            p.x = x + random.uniform(-spread, spread)
            p.y = y + random.uniform(-spread, spread)
            p.vx = vx + random.uniform(-spread*0.5, spread*0.5)
            p.vy = vy + random.uniform(-spread*0.5, spread*0.5)
            p.life = life + random.uniform(-life*0.2, life*0.2)
            p.max_life = p.life
            p.color = color
            p.end_color = end_color if end_color else color
            p.size = size + random.uniform(-size*0.3, size*0.3)
            p.end_size = end_size
            p.gravity = gravity
            p.ptype = ptype
            p.angle = random.uniform(0, math.pi*2)
            p.spin = spin + random.uniform(-spin*0.5, spin*0.5)
            self.active_list.append(p)

    def emit_burst(self, x, y, count, speed, life, color, end_color=None, size=4, gravity=0):
        for i in range(count):
            angle = random.uniform(0, math.pi*2)
            spd = random.uniform(speed*0.5, speed)
            vx = math.cos(angle)*spd
            vy = math.sin(angle)*spd
            self.emit(x, y, vx, vy, life, color, end_color, size, 0, gravity)

    def emit_explosion(self, x, y, color1=(255,200,50), color2=(200,50,0), count=30):
        self.emit_burst(x, y, count, 180, 0.6, color1, color2, 8, gravity=60)
        self.emit_burst(x, y, count//2, 80, 0.4, (255,255,200), (200,100,0), 4, gravity=40)

    def emit_blood(self, x, y, count=12):
        self.emit_burst(x, y,
I'll build the remaining files systematically. Let me implement all the missing components.

```python
# filename: camera.py
import pygame
from settings import *

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_x = 0
        self.shake_y = 0
        self.lerp_speed = 8.0

    def update(self, target_x, target_y, dt):
        self.target_x = target_x - VIEWPORT_W / 2
        self.target_y = target_y - VIEWPORT_H / 2
        self.target_x = max(0, min(self.target_x, ARENA_W - VIEWPORT_W))
        self.target_y = max(0, min(self.target_y, ARENA_H - VIEWPORT_H))
        self.x += (self.target_x - self.x) * self.lerp_speed * dt
        self.y += (self.target_y - self.y) * self.lerp_speed * dt
        if self.shake_duration > 0:
            self.shake_duration -= dt
            import random
            s = self.shake_intensity * (self.shake_duration / max(self.shake_duration + 0.01, 0.3))
            self.shake_x = random.randint(-int(s), int(s))
            self.shake_y = random.randint(-int(s), int(s))
        else:
            self.shake_x = 0
            self.shake_y = 0

    def shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration

    def world_to_screen(self, wx, wy):
        return (wx - self.x + self.shake_x, wy - self.y + self.shake_y)

    def screen_to_world(self, sx, sy):
        return (sx + self.x - self.shake_x, sy + self.y - self.shake_y)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), VIEWPORT_W, VIEWPORT_H)