import pygame
import math
import random

class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=3, gravity=0, fade=True, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.max_size = size
        self.gravity = gravity
        self.fade = fade
        self.shrink = shrink
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1
        if self.life <= 0:
            self.alive = False
        if self.shrink:
            self.size = self.max_size * (self.life / self.max_life)

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        if not (0 <= sx <= surface.get_width() and 0 <= sy <= surface.get_height()):
            return
        r, g, b = self.color
        if self.fade:
            alpha = self.life / self.max_life
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
        s = max(1, int(self.size))
        pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy)), s)

class TextParticle:
    def __init__(self, x, y, text, color=(255,255,100), size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.life = 80
        self.max_life = 80
        self.vy = -1.5
        self.alive = True
        self.font = pygame.font.SysFont("arial", size, bold=True)

    def update(self):
        self.y += self.vy
        self.vy *= 0.97
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        alpha = self.life / self.max_life
        r, g, b = self.color
        surf = self.font.render(self.text, True, (int(r*alpha), int(g*alpha), int(b*alpha)))
        surface.blit(surf, (int(sx) - surf.get_width()//2, int(sy)))

class ParticleEngine:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color_range, speed_range=(1,4),
              life_range=(20,60), size_range=(2,5), gravity=0, angle_range=(0, 360)):
        for _ in range(count):
            angle = math.radians(random.uniform(*angle_range))
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice(color_range) if isinstance(color_range, list) else color_range
            life = random.randint(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, vx, vy, color, life, size, gravity))

    def emit_explosion(self, x, y, count=30, color=None):
        if color is None:
            colors = [(255,200,0),(255,120,0),(255,60,0),(200,200,200)]
        else:
            colors = [color]
        self.emit(x, y, count, colors, (2,8), (20,60), (3,8), gravity=0.1)

    def emit_blood(self, x, y, count=15):
        colors = [(200,0,0),(180,20,0),(255,30,0)]
        self.emit(x, y, count, colors, (1,5), (20,50), (2,5), gravity=0.2)

    def emit_sparks(self, x, y, count=10, color=(255,220,80)):
        self.emit(x, y, count, [color], (2,6), (10,30), (1,3))

    def emit_dust(self, x, y, count=8):
        colors = [(180,160,130),(200,180,150),(150,140,120)]
        self.emit(x, y, count, colors, (0.5,2), (20,40), (2,4))

    def add_text(self, x, y, text, color=(255,255,100), size=20):
        self.particles.append(TextParticle(x, y, text, color, size))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, cam):
        for p in self.particles:
            p.draw(surface, cam)