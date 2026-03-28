import pygame
import random
import math
from utils import clamp

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','gravity','fade','shrink']
    def __init__(self, x, y, vx, vy, life, color, size=4, gravity=0, fade=True, shrink=True):
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.life = life; self.max_life = life
        self.color = color; self.size = size
        self.gravity = gravity; self.fade = fade; self.shrink = shrink

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.vx *= (1 - 2 * dt)
        self.life -= dt
        return self.life > 0

    def draw(self, surface, cam):
        t = self.life / self.max_life
        alpha = int(255 * t) if self.fade else 255
        size = max(1, int(self.size * t)) if self.shrink else max(1, int(self.size))
        sx, sy = cam.apply(self.x, self.y)
        r, g, b = self.color[:3]
        color = (clamp(r,0,255), clamp(g,0,255), clamp(b,0,255), alpha)
        surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size, size), size)
        surface.blit(surf, (sx - size, sy - size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color, speed=80, life=0.6, size=4, gravity=0, spread=math.pi*2, angle=0, fade=True, shrink=True):
        for _ in range(count):
            a = angle + random.uniform(-spread/2, spread/2)
            spd = random.uniform(speed*0.4, speed*1.2)
            vx = math.cos(a) * spd
            vy = math.sin(a) * spd
            l = life * random.uniform(0.7, 1.3)
            r,g,b = color[:3]
            c = (clamp(r+random.randint(-20,20),0,255),
                 clamp(g+random.randint(-20,20),0,255),
                 clamp(b+random.randint(-20,20),0,255))
            self.particles.append(Particle(x, y, vx, vy, l, c, size, gravity, fade, shrink))

    def emit_blood(self, x, y, count=12):
        self.emit(x, y, count, (200,30,30), speed=120, life=0.5, size=5, gravity=200)

    def emit_explosion(self, x, y, count=30):
        self.emit(x, y, count//2, (255,200,50), speed=200, life=0.8, size=8, gravity=50)
        self.emit(x, y, count//2, (255,80,20), speed=150, life=0.6, size=5, gravity=80)

    def emit_sparks(self, x, y, count=8, color=(255,255,100)):
        self.emit(x, y, count, color, speed=150, life=0.4, size=3, gravity=100)

    def emit_dash(self, x, y, color=(100,180,255)):
        self.emit(x, y, 6, color, speed=40, life=0.3, size=6, fade=True)

    def emit_coin(self, x, y):
        self.emit(x, y, 8, (255,220,50), speed=80, life=0.5, size=4)

    def emit_heal(self, x, y):
        self.emit(x, y, 10, (50,255,100), speed=60, life=0.7, size=5, gravity=-50)

    def emit_lava(self, x, y):
        self.emit(x, y, 3, (255,100,20), speed=60, life=0.4, size=5, gravity=-30)

    def emit_poison(self, x, y):
        self.emit(x, y, 3, (80,220,80), speed=40, life=0.5, size=4, gravity=-20)

    def emit_ice(self, x, y):
        self.emit(x, y, 4, (180,220,255), speed=50, life=0.3, size=3)

    def emit_chain(self, x1, y1, x2, y2):
        steps = 6
        for i in range(steps):
            t = i / steps
            px = x1 + (x2-x1)*t + random.uniform(-10,10)
            py = y1 + (y2-y1)*t + random.uniform(-10,10)
            self.emit(px, py, 2, (255,255,100), speed=20, life=0.2, size=3)

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface, cam):
        for p in self.particles:
            p.draw(surface, cam)

    def clear(self):
        self.particles.clear()