import pygame
import random
import math
from utils import vec2_len, clamp

class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','gravity','fade']
    def __init__(self, x, y, vx, vy, life, color, size=4, gravity=0, fade=True):
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.life = life; self.max_life = life
        self.color = color; self.size = size
        self.gravity = gravity; self.fade = fade

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, speed_range, color, life_range=(0.3,0.8),
              size=4, gravity=0, angle_range=(0, math.pi*2), fade=True, color_var=20):
        for _ in range(count):
            angle = random.uniform(*angle_range)
            spd = random.uniform(*speed_range)
            vx = math.cos(angle)*spd
            vy = math.sin(angle)*spd
            life = random.uniform(*life_range)
            r = clamp(color[0]+random.randint(-color_var,color_var),0,255)
            g = clamp(color[1]+random.randint(-color_var,color_var),0,255)
            b = clamp(color[2]+random.randint(-color_var,color_var),0,255)
            self.particles.append(Particle(x,y,vx,vy,life,(r,g,b),size,gravity,fade))

    def emit_blood(self, x, y, count=12):
        self.emit(x, y, count, (40,200), (180,20,20), life_range=(0.2,0.6),
                  size=3, gravity=120)

    def emit_explosion(self, x, y, count=30, color=(255,120,30)):
        self.emit(x, y, count, (80,350), color, life_range=(0.3,0.9),
                  size=5, gravity=20, color_var=40)
        self.emit(x, y, count//2, (20,100), (255,255,200), life_range=(0.1,0.4), size=3)

    def emit_sparks(self, x, y, count=8, color=(255,220,50)):
        self.emit(x, y, count, (60,250), color, life_range=(0.2,0.5), size=2)

    def emit_smoke(self, x, y, count=5):
        self.emit(x, y, count, (10,60), (100,100,100), life_range=(0.5,1.5), size=6, fade=True)

    def emit_lava(self, x, y):
        self.emit(x, y, 3, (30,100), (220,80,0), life_range=(0.3,0.7), size=4, gravity=-40)

    def emit_ice(self, x, y, count=8):
        self.emit(x, y, count, (30,150), (180,220,255), life_range=(0.3,0.8), size=3)

    def emit_poison(self, x, y, count=5):
        self.emit(x, y, count, (20,80), (80,200,50), life_range=(0.4,1.0), size=3)

    def emit_dash_afterimage(self, x, y, color=(100,180,255)):
        self.emit(x, y, 6, (5,30), color, life_range=(0.1,0.3), size=8, fade=True)

    def emit_coin(self, x, y):
        self.emit(x, y, 5, (30,120), (255,200,0), life_range=(0.2,0.5), size=3)

    def update(self, dt):
        live = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravity * dt
            p.vx *= 0.97
            live.append(p)
        self.particles = live

    def draw(self, surface, cam_offset):
        ox, oy = cam_offset
        for p in self.particles:
            sx = int(p.x - ox)
            sy = int(p.y - oy)
            if sx < -20 or sx > 1300 or sy < -20 or sy > 740:
                continue
            alpha = p.life / p.max_life if p.fade else 1.0
            size = max(1, int(p.size * alpha))
            col = (int(p.color[0]*alpha), int(p.color[1]*alpha), int(p.color[2]*alpha))
            pygame.draw.circle(surface, col, (sx, sy), size)