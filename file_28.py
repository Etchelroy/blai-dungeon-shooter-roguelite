import pygame
import random
import math
from utils import clamp

MAX_PARTICLES = 2000

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','gravity','fade','shrink']
    def __init__(self):
        self.x=self.y=self.vx=self.vy=self.life=self.max_life=0.0
        self.color=(255,255,255)
        self.size=4.0
        self.gravity=0.0
        self.fade=True
        self.shrink=True

class ParticlePool:
    def __init__(self):
        self.pool = [Particle() for _ in range(MAX_PARTICLES)]
        self.active = []
        self.free = list(self.pool)

    def spawn(self, x, y, vx, vy, life, color, size=4, gravity=0, fade=True, shrink=True):
        if not self.free:
            return
        p = self.free.pop()
        p.x, p.y = x, y
        p.vx, p.vy = vx, vy
        p.life = p.max_life = life
        p.color = color
        p.size = size
        p.gravity = gravity
        p.fade = fade
        p.shrink = shrink
        self.active.append(p)

    def burst(self, x, y, count, color, speed=120, life=0.5, size=4, gravity=80, spread=math.pi*2):
        for _ in range(count):
            a = random.uniform(0, spread)
            s = random.uniform(speed*0.3, speed)
            self.spawn(x, y, math.cos(a)*s, math.sin(a)*s, random.uniform(life*0.5, life), color, size+random.uniform(-1,1), gravity)

    def update(self, dt):
        dead = []
        for p in self.active:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravity * dt
            p.vx *= (1 - 3*dt)
            p.life -= dt
            if p.life <= 0:
                dead.append(p)
        for p in dead:
            self.active.remove(p)
            self.free.append(p)

    def draw(self, surface, cam_x, cam_y):
        for p in self.active:
            frac = clamp(p.life / p.max_life, 0, 1)
            alpha = int(255 * frac) if p.fade else 255
            size = max(1, int(p.size * frac) if p.shrink else int(p.size))
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            if -size <= sx <= 1280+size and -size <= sy <= 720+size:
                c = (clamp(p.color[0],0,255), clamp(p.color[1],0,255), clamp(p.color[2],0,255))
                if size == 1:
                    if 0 <= sx < 1280 and 0 <= sy < 720:
                        surface.set_at((sx,sy), c)
                else:
                    pygame.draw.circle(surface, c, (sx,sy), size)