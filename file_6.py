import pygame, math, random
from src.utils import vec2_norm, clamp

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','gravity','fade','shrink']
    def __init__(self, x, y, vx, vy, life, color, size=3, gravity=0, fade=True, shrink=True):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.life=life; self.max_life=life
        self.color=color; self.size=size
        self.gravity=gravity; self.fade=fade; self.shrink=shrink

class ParticleSystem:
    MAX = 2000
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=6, speed=80, spread=math.pi*2,
              angle=0, life=0.6, size=3, gravity=0, fade=True, shrink=True):
        for _ in range(count):
            a = angle + random.uniform(-spread/2, spread/2)
            spd = random.uniform(speed*0.5, speed*1.5)
            vx = math.cos(a)*spd; vy = math.sin(a)*spd
            lt = life * random.uniform(0.7, 1.3)
            if len(self.particles) < self.MAX:
                self.particles.append(Particle(x, y, vx, vy, lt, color, size, gravity, fade, shrink))

    def emit_burst(self, x, y, color, count=12, speed=120, life=0.5, size=4):
        self.emit(x, y, color, count, speed, life=life, size=size, gravity=60)

    def emit_sparks(self, x, y, color, count=8):
        self.emit(x, y, color, count, speed=150, life=0.4, size=2, gravity=80)

    def emit_blood(self, x, y, count=10):
        self.emit(x, y, (180,20,20), count, speed=100, life=0.5, size=3, gravity=120)

    def emit_smoke(self, x, y, count=5):
        c = random.randint(80,120)
        self.emit(x, y, (c,c,c), count, speed=30, life=1.2, size=5, gravity=-10, shrink=False)

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravity * dt
            p.vx *= (1 - dt*3)
            alive.append(p)
        self.particles = alive

    def draw(self, surf, cam_x, cam_y):
        for p in self.particles:
            t = p.life / p.max_life
            alpha = int(255*t) if p.fade else 255
            sz = max(1, int(p.size * t)) if p.shrink else p.size
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            if -sz < sx < surf.get_width()+sz and -sz < sy < surf.get_height()+sz:
                c = list(p.color)
                while len(c) < 3: c.append(255)
                col = (clamp(c[0],0,255), clamp(c[1],0,255), clamp(c[2],0,255))
                pygame.draw.circle(surf, col, (sx, sy), sz)