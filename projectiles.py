import pygame
import math
import random
from constants import *
from utils import *
from assets import get_projectile_surf

class Projectile:
    def __init__(self, x, y, vx, vy, damage, ptype='bullet', owner='player',
                 pierce=0, aoe=0, lifetime=3.0, size=8):
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.damage = damage
        self.ptype = ptype
        self.owner = owner
        self.pierce = pierce
        self.aoe = aoe
        self.lifetime = lifetime
        self.size = size
        self.alive = True
        self.hit_set = set()
        self.surf = get_projectile_surf(ptype, size)

    def update(self, dt, arena=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        if arena and arena.is_wall_at(self.x, self.y):
            self.alive = False

    def draw(self, surface, cam_offset):
        ox, oy = cam_offset
        sx = int(self.x - ox)
        sy = int(self.y - oy)
        surface.blit(self.surf, (sx - self.size//2, sy - self.size//2))

class FlameProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage):
        super().__init__(x, y, vx, vy, damage, 'flame', size=10, lifetime=0.6)
        self.dot_damage = 5
        self.dot_duration = 2.0

    def update(self, dt, arena=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.97
        self.vy *= 0.97
        self.size = max(4, int(10 * self.lifetime / 0.6))
        if arena and arena.is_wall_at(self.x, self.y):
            self.alive = False

class BoomerangProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, owner_ref):
        super().__init__(x, y, vx, vy, damage, 'boomerang', size=12, lifetime=2.0)
        self.owner_ref = owner_ref
        self.returning = False
        self.max_dist = 300
        self.start_x = x
        self.start_y = y
        self.hit_set_return = set()

    def update(self, dt, arena=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        if not self.returning:
            dist = vec2_dist((self.start_x, self.start_y), (self.x, self.y))
            if dist >= self.max_dist:
                self.returning = True
        if self.returning:
            tx = self.owner_ref.x - self.x
            ty = self.owner_ref.y - self.y
            d = max(1, math.sqrt(tx*tx+ty*ty))
            speed = 380
            self.vx = (tx/d)*speed
            self.vy = (ty/d)*speed
            if d < 20:
                self.alive = False
                return
        self.x += self.vx * dt
        self.y += self.vy * dt
        if arena and arena.is_wall_at(self.x, self.y):
            if not self.returning:
                self.returning = True
            else:
                self.alive = False

class ChainProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, bounces=3):
        super().__init__(x, y, vx, vy, damage, 'chain', size=10, lifetime=3.0)
        self.bounces_left = bounces
        self.chain_targets = set()

    def bounce_to(self, enemies, current_target=None):
        best = None
        best_dist = 300
        for e in enemies:
            if id(e) in self.chain_targets:
                continue
            if not e.alive:
                continue
            d = vec2_dist((self.x, self.y), (e.x, e.y))
            if d < best_dist:
                best_dist = d
                best = e
        if best:
            self.chain_targets.add(id(best))
            angle = angle_to((self.x, self.y), (best.x, best.y))
            speed = vec2_len((self.vx, self.vy))
            self.vx = math.cos(angle)*speed
            self.vy = math.sin(angle)*speed
            self.bounces_left -= 1
            return True
        return False

class ProjectileManager:
    def __init__(self):
        self.projectiles = []

    def add(self, proj):
        self.projectiles.append(proj)

    def update(self, dt, arena=None):
        for p in self.projectiles:
            p.update(dt, arena)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def check_hits(self, targets, owner_filter):
        hits = []
        for p in self.projectiles:
            if not p.alive:
                continue
            if p.owner != owner_filter:
                continue
            for t in targets:
                if not t.alive:
                    continue
                if id(t) in p.hit_set:
                    continue
                if circles_overlap(p.x, p.y, p.size//2, t.x, t.y, t.radius):
                    hits.append((p, t))
                    p.hit_set.add(id(t))
                    if p.pierce <= 0:
                        p.alive = False
                    else:
                        p.pierce -= 1
        return hits

    def draw(self, surface, cam_offset):
        for p in self.projectiles:
            if p.alive:
                p.draw(surface, cam_offset)