import pygame
import math
import random
from constants import *
from utils import normalize, distance, angle_to, vec_from_angle
import assets

class Projectile:
    def __init__(self, x, y, vx, vy, damage, owner, ptype="bullet",
                 pierce=False, lifetime=2.0, aoe_radius=0, homing=False):
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.damage = damage
        self.owner = owner
        self.ptype = ptype
        self.pierce = pierce
        self.lifetime = lifetime
        self.aoe_radius = aoe_radius
        self.homing = homing
        self.alive = True
        self.hit_enemies = set()
        self.surf = assets.get_projectile_surf(ptype)
        self.angle = math.atan2(vy, vx)
        self.return_target = None
        self.bounce_count = 0

    def update(self, dt, enemies=None, walls=None):
        if not self.alive:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        if self.homing and enemies:
            closest = None
            best = 999999
            for e in enemies:
                if not e.alive:
                    continue
                d = distance((self.x, self.y), (e.x, e.y))
                if d < best:
                    best = d
                    closest = e
            if closest and best < 300:
                tx, ty = closest.x, closest.y
                dx, dy = normalize((tx - self.x, ty - self.y))
                speed = math.hypot(self.vx, self.vy)
                self.vx += dx * 400 * dt
                self.vy += dy * 400 * dt
                spd = math.hypot(self.vx, self.vy)
                if spd > speed * 1.5:
                    self.vx = self.vx / spd * speed * 1.5
                    self.vy = self.vy / spd * speed * 1.5
        if self.return_target:
            tx, ty = self.return_target
            dx, dy = normalize((tx - self.x, ty - self.y))
            speed = math.hypot(self.vx, self.vy)
            if speed < 200:
                speed = 200
            self.vx = dx * speed
            self.vy = dy * speed
            if distance((self.x, self.y), (tx, ty)) < 20:
                self.alive = False
                return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle = math.atan2(self.vy, self.vx)

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(self.x, self.y)
        rot, rect = _rot_surf(self.surf, self.angle, (sx, sy))
        surface.blit(rot, rect)

    def get_rect(self):
        w, h = self.surf.get_size()
        return pygame.Rect(self.x - w//2, self.y - h//2, w, h)

def _rot_surf(surf, angle, pos):
    rotated = pygame.transform.rotate(surf, -math.degrees(angle))
    rect = rotated.get_rect(center=pos)
    return rotated, rect

class FlameParticle:
    def __init__(self, x, y, angle):
        self.x = x; self.y = y
        spread = random.uniform(-0.4, 0.4)
        spd = random.uniform(120, 200)
        a = angle + spread
        self.vx = math.cos(a) * spd
        self.vy = math.sin(a) * spd
        self.life = random.uniform(0.2, 0.5)
        self.max_life = self.life
        self.alive = True
        self.damage = 0
        self.owner = "player"
        self.ptype = "flame"
        self.hit_enemies = set()
        self.damage_tick = 0.08
        self.damage_timer = 0.0
        self.aoe_radius = 0
        self.pierce = True

    def update(self, dt, enemies=None, walls=None):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (1 - dt)
        self.vy *= (1 - dt)
        self.damage_timer -= dt

    def get_rect(self):
        return pygame.Rect(self.x - 8, self.y - 8, 16, 16)

    def draw(self, surface, cam):
        if not self.alive:
            return
        t = self.life / self.max_life
        sx, sy = cam.apply(self.x, self.y)
        alpha = int(200 * t)
        size = int(10 * t) + 3
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        r = int(255)
        g = int(80 * t)
        pygame.draw.circle(s, (r, g, 20, alpha), (size, size), size)
        surface.blit(s, (sx - size, sy - size))