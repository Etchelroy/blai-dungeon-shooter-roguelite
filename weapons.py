import pygame
import math
import random
from settings import *

class Projectile:
    def __init__(self, x, y, vx, vy, damage, owner, color=(255, 220, 50),
                 radius=5, lifetime=2.0, pierce=0, is_enemy=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.owner = owner
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.pierce = pierce
        self.is_enemy = is_enemy
        self.alive = True
        self.hit_set = set()
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, dt, tilemap):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        col = int(self.x // (TILE_SIZE * 3))
        row = int(self.y // (TILE_SIZE * 3))
        if tilemap.is_solid(col, row):
            self.alive = False

    def render(self, screen, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        for i, (tx, ty) in enumerate(self.trail):
            tsx, tsy = camera.world_to_screen(tx, ty)
            alpha = int(180 * (i / max(len(self.trail), 1)))
            r = max(1, self.radius - (len(self.trail) - i))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
            screen.blit(s, (tsx - r, tsy - r))
        pygame.draw.circle(screen, self.color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), max(1, self.radius - 2))


class BouncingProjectile(Projectile):
    def __init__(self, *args, bounces=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.bounces = bounces

    def update(self, dt, tilemap):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        col_x = int(nx // (TILE_SIZE * 3))
        row_x = int(self.y // (TILE_SIZE * 3))
        col_y = int(self.x // (TILE_SIZE * 3))
        row_y = int(ny // (TILE_SIZE * 3))
        bounced = False
        if tilemap.is_solid(col_x, row_x):
            self.vx = -self.vx
            nx = self.x
            bounced = True
        if tilemap.is_solid(col_y, row_y):
            self.vy = -self.vy
            ny = self.y
            bounced = True
        if bounced:
            self.bounces -= 1
            if self.bounces <= 0:
                self.alive = False
                return
        self.x = nx
        self.y = ny


class HomingProjectile(Projectile):
    def __init__(self, *args, target=None, turn_speed=4.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.turn_speed = turn_speed

    def update(self, dt, tilemap):
        if self.target and hasattr(self.target, 'alive') and self.target.alive:
            tx = self.target.x - self.x
            ty = self.target.y - self.y
            dist = math.hypot(tx, ty)
            if dist > 0:
                tx /= dist
                ty /= dist
                speed = math.hypot(self.vx, self.vy)
                cx = self.vx / max(speed, 0.01)
                cy = self.vy / max(speed, 0.01)
                cx += tx * self.turn_speed * dt
                cy += ty * self.turn_speed * dt
                mag = math.hypot(cx, cy)
                if mag > 0:
                    self.vx = cx / mag * speed
                    self.vy = cy / mag * speed
        super().update(dt, tilemap)


class ChainLightning:
    def __init__(self, x, y, targets, damage, jumps=3):
        self.segments = []
        self.damage = damage
        self.lifetime = 0.3
        self.alive = True
        hit = set()
        cx, cy = x, y
        remaining = list(targets)
        for _ in range(jumps):
            best = None
            bd = 999999
            for t in remaining:
                if id(t) in hit:
                    continue
                d = math.hypot(t.x - cx, t.y - cy)
                if d < 200 and d < bd:
                    bd = d
                    best = t
            if best is None:
                break
            self.segments.append(((cx, cy), (best.x, best.y)))
            hit.add(id(best))
            best.take_damage(damage)
            cx, cy = best.x, best.y

    def update(self, dt, tilemap):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def render(self, screen, camera):
        for (x1, y1), (x2, y2) in self.segments:
            sx1, sy1 = camera.world_to_screen(x1, y1)
            sx2, sy2 = camera.world_to_screen(x2, y2)
            for _ in range(3):
                jx = random.randint(-6, 6)
                jy = random.randint(-6, 6)
                pygame.draw.line(screen, (180, 180, 255), (int(sx1), int(sy1)),
                                 (int((sx1 + sx2) / 2 + jx), int((sy1 + sy2) / 2 + jy)), 2)
                pygame.draw.line(screen, (180, 180, 255),
                                 (int((sx1 + sx2) / 2 + jx), int((sy1 + sy2) / 2 + jy)),
                                 (int(sx2), int(sy2)), 2)
            pygame.draw.line(screen, (220, 220, 255), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 1)


WEAPON_DEFS = {
    'pistol':     {'name': 'Pistol',      'damage': 18, 'speed': 600, 'cooldown': 0.25, 'ammo': -1,  'color': (255, 220, 80),  'radius': 4},
    'shotgun':    {'name': 'Shotgun',     'damage': 14, 'speed': 480, 'cooldown': 0.6,  'ammo': 40,  'color': (255, 160, 60),  'radius': 5, 'pellets': 7, 'spread': 0.35},
    'rifle':      {'name': 'Rifle',       'damage': 35, 'speed': 900, 'cooldown': 0.15, 'ammo': 80,  'color': (100, 220, 255), 'radius': 3, 'pierce': 2},
    'launcher':   {'name': 'Launcher',    'damage': 60, 'speed': 380, 'cooldown': 1.0,  'ammo': 20,  'color': (255, 100, 40),  'radius': 8, 'aoe': 80},
    'chaingun':   {'name': 'Chaingun',    'damage': 10, 'speed': 700, 'cooldown': 0.07, 'ammo': 200, 'color': (255, 255, 100), 'radius': 3, 'spread': 0.08},
    'lightning':  {'name': 'Lightning',   'damage': 25, 'speed': 0,   'cooldown': 0.4,  'ammo': 60,  'color': (180, 180, 255), 'radius': 0, 'chain': 4},
    'boomerang':  {'name': 'Boomerang',   'damage': 30, 'speed': 500, 'cooldown': 0.8,  'ammo': -1,  'color': (255, 200, 80),  'radius': 7, 'returning': True},
    'flamethrower':{'name':'Flamethrower','damage': 8,  'speed': 300, 'cooldown': 0.05, 'ammo': 150, 'color': (255, 80, 20),   'radius': 5, 'cone': True, 'dot': 2},
}


class Weapon:
    def __init__(self, weapon_id):
        self.id = weapon_id
        data = WEAPON_DEFS[weapon_id]
        self.name = data['name']
        self.damage = data['damage']
        self.speed = data['speed']
        self.base_cooldown = data['cooldown']
        self.cooldown = 0.0
        self.ammo = data['ammo']
        self.max_ammo = data['ammo']
        self.color = data['color']
        self.radius = data['radius']
        self.pellets = data.get('pellets', 1)
        self.spread = data.get('spread', 0.0)
        self.pierce = data.get('pierce', 0)
        self.aoe = data.get('aoe', 0)
        self.chain = data.get('chain', 0)
        self.returning = data.get('returning', False)
        self.cone = data.get('cone', False)
        self.dot = data.get('dot', 0)
        self.damage_mult = 1.0
        self.cooldown_mult = 1.0

    def can_fire(self):
        return self.cooldown <= 0 and (self.ammo == -1 or self.ammo > 0)

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

    def fire(self, x, y, angle, owner, enemies=None):
        if not self.can_fire():
            return []
        cd = self.base_cooldown * self.cooldown_mult
        self.cooldown = cd
        if self.ammo > 0:
            self.ammo -= 1
        dmg = int(self.damage * self.damage_mult)
        projectiles = []

        if self.id == 'lightning' and enemies:
            nearby = [e for e in enemies if math.hypot(e.x - x, e.y - y) < 250]
            if nearby:
                proj = ChainLightning(x, y, nearby, dmg, self.chain)
                return [proj]
            return []

        for i in range(self.pellets):
            a = angle + (random.random() - 0.5) * self.spread * 2 if self.spread else angle
            if self.pellets > 1:
                a = angle + (i - self.pellets // 2) * (self.spread / max(self.pellets - 1, 1)) * 2
                a += (random.random() - 0.5) * 0.05
            vx = math.cos(a) * self.speed
            vy = math.sin(a) * self.speed
            lt = 2.5 if self.id != 'flamethrower' else 0.5
            if self.returning:
                proj = BouncingProjectile(x, y, vx, vy, dmg, owner, self.color,
                                          self.radius, lt, self.pierce)
                proj.bounces = 5
            else:
                proj = Projectile(x, y, vx, vy, dmg, owner, self.color,
                                  self.radius, lt, self.pierce)
            proj.aoe = self.aoe
            proj.dot = self.dot
            projectiles.append(proj)
        return projectiles