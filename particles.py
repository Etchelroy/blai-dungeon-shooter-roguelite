import pygame
import random
import math
from constants import *
from utils import clamp

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','gravity','fade','shrink']
    def __init__(self, x, y, vx, vy, life, color, size=4, gravity=0, fade=True, shrink=True):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.life = life; self.max_life = life; self.color = color
        self.size = size; self.gravity = gravity; self.fade = fade; self.shrink = shrink

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=6, speed=80, life=0.5, size=4, spread=math.pi*2, angle=0, gravity=120, shrink=True):
        for _ in range(min(count, MAX_PARTICLES - len(self.particles))):
            a = angle + random.uniform(-spread/2, spread/2)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(a) * spd
            vy = math.sin(a) * spd
            l = life * random.uniform(0.7, 1.3)
            c = (clamp(color[0]+random.randint(-20,20),0,255),
                 clamp(color[1]+random.randint(-20,20),0,255),
                 clamp(color[2]+random.randint(-20,20),0,255))
            self.particles.append(Particle(x, y, vx, vy, l, c, size, gravity, True, shrink))

    def emit_blood(self, x, y, count=10):
        self.emit(x, y, (200, 30, 30), count, speed=120, life=0.6, size=5, gravity=200)

    def emit_explosion(self, x, y, radius=60):
        self.emit(x, y, (255, 180, 50), 20, speed=200, life=0.8, size=8, gravity=50)
        self.emit(x, y, (255, 100, 20), 15, speed=150, life=0.5, size=5, gravity=80)
        self.emit(x, y, (200, 200, 200), 10, speed=100, life=1.0, size=3, gravity=30)

    def emit_spark(self, x, y, color=YELLOW, count=8):
        self.emit(x, y, color, count, speed=150, life=0.3, size=3, gravity=300)

    def emit_smoke(self, x, y, count=5):
        self.emit(x, y, (150,150,150), count, speed=40, life=1.2, size=8, gravity=-20, shrink=False)

    def emit_lava(self, x, y):
        self.emit(x, y, (255,100,20), 3, speed=60, life=0.5, size=5, gravity=80)

    def emit_poison(self, x, y):
        self.emit(x, y, (60,200,60), 4, speed=50, life=0.6, size=4, gravity=0)

    def emit_ice(self, x, y):
        self.emit(x, y, (180,220,255), 5, speed=80, life=0.4, size=3, gravity=100)

    def emit_coin(self, x, y):
        self.emit(x, y, GOLD, 6, speed=100, life=0.4, size=4, gravity=200)

    def emit_dash(self, x, y, color=(100,180,255)):
        self.emit(x, y, color, 8, speed=60, life=0.25, size=6, gravity=0, shrink=True)

    def emit_heal(self, x, y):
        self.emit(x, y, (50,255,100), 8, speed=60, life=0.7, size=5, gravity=-60)

    def emit_chain(self, x1, y1, x2, y2):
        steps = 8
        for i in range(steps):
            t = i / steps
            px = x1 + (x2-x1)*t + random.randint(-8,8)
            py = y1 + (y2-y1)*t + random.randint(-8,8)
            self.emit(px, py, PURPLE, 2, speed=20, life=0.2, size=3, gravity=0)

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravity * dt
            p.vx *= 0.97
            alive.append(p)
        self.particles = alive

    def draw(self, surface, camera):
        cam_rect = camera.get_rect()
        for p in self.particles:
            if not cam_rect.collidepoint(p.x, p.y):
                continue
            sx, sy = camera.world_to_screen(p.x, p.y)
            t = p.life / p.max_life
            alpha = int(255 * t) if p.fade else 255
            size = max(1, int(p.size * t)) if p.shrink else max(1, int(p.size))
            c = p.color
            if size <= 2:
                pygame.draw.circle(surface, c, (int(sx), int(sy)), size)
            else:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*c, alpha), (size, size), size)
                surface.blit(s, (int(sx)-size, int(sy)-size))