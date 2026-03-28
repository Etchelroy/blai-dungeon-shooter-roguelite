import pygame
import math
import random

class Projectile:
    def __init__(self, x, y, vx, vy, damage, color=(255,220,0), radius=5,
                 pierce=False, max_pierce=1, life=120, owner="player",
                 aoe_radius=0, slow=0, burn=0, chain=0, homing=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.color = color
        self.radius = radius
        self.pierce = pierce
        self.pierce_count = 0
        self.max_pierce = max_pierce
        self.life = life
        self.alive = True
        self.owner = owner
        self.aoe_radius = aoe_radius
        self.slow = slow
        self.burn = burn
        self.chain = chain
        self.chain_count = 0
        self.homing = homing
        self.homing_target = None
        self.hit_enemies = set()
        self.trail = []

    def update(self, enemies=None):
        if self.homing and enemies:
            best = None
            best_dist = 300
            for e in enemies:
                if not e.alive:
                    continue
                d = math.hypot(e.x - self.x, e.y - self.y)
                if d < best_dist:
                    best_dist = d
                    best = e
            if best:
                dx = best.x - self.x
                dy = best.y - self.y
                d = math.hypot(dx, dy) + 0.001
                self.vx += (dx/d) * 0.5
                self.vy += (dy/d) * 0.5
                speed = math.hypot(self.vx, self.vy)
                max_speed = 8
                if speed > max_speed:
                    self.vx = self.vx/speed * max_speed
                    self.vy = self.vy/speed * max_speed

        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, cam):
        for i, (tx, ty) in enumerate(self.trail):
            sx, sy = cam.apply(tx, ty)
            alpha = (i / len(self.trail)) * 0.5
            r, g, b = self.color
            c = (int(r*alpha), int(g*alpha), int(b*alpha))
            s = max(1, int(self.radius * alpha))
            pygame.draw.circle(surface, c, (int(sx), int(sy)), s)

        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)

    def check_hit(self, entity):
        if id(entity) in self.hit_enemies:
            return False
        d = math.hypot(entity.x - self.x, entity.y - self.y)
        if d < self.radius + entity.radius:
            self.hit_enemies.add(id(entity))
            if not self.pierce or self.pierce_count >= self.max_pierce:
                self.alive = False
            else:
                self.pierce_count += 1
            return True
        return False

class BombProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, aoe_radius=80):
        super().__init__(x, y, vx, vy, damage, (255,100,0), 8, life=80, aoe_radius=aoe_radius)
        self.fuse = 80

    def update(self, enemies=None):
        super().update(enemies)
        self.fuse -= 1
        if self.fuse <= 0:
            self.alive = False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pulse = abs(math.sin(self.fuse * 0.2))
        r = int(255 * pulse)
        pygame.draw.circle(surface, (r, 100, 0), (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, (255, 200, 0), (int(sx), int(sy)), self.radius // 2)

class ReturnProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, owner_ref):
        super().__init__(x, y, vx, vy, damage, (0, 220, 255), 7, life=200, pierce=True, max_pierce=99)
        self.owner_ref = owner_ref
        self.returning = False
        self.out_timer = 30

    def update(self, enemies=None):
        self.out_timer -= 1
        if self.out_timer <= 0:
            self.returning = True
        if self.returning:
            dx = self.owner_ref.x - self.x
            dy = self.owner_ref.y - self.y
            d = math.hypot(dx, dy) + 0.001
            speed = 10
            self.vx = dx/d * speed
            self.vy = dy/d * speed
            if d < 20:
                self.alive = False
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.alive = False

class LaserBeam:
    def __init__(self, x, y, angle, damage, length=400, width=6, duration=30, owner="player"):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.length = length
        self.width = width
        self.duration = duration
        self.life = duration
        self.alive = True
        self.owner = owner
        self.ex = x + math.cos(angle) * length
        self.ey = y + math.sin(angle) * length
        self.hit_enemies = set()

    def update(self, enemies=None):
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def check_hit(self, entity):
        if id(entity) in self.hit_enemies:
            return False
        # Line-circle intersection
        dx = self.ex - self.x
        dy = self.ey - self.y
        fx = self.x - entity.x
        fy = self.y - entity.y
        a = dx*dx + dy*dy
        b = 2*(fx*dx + fy*dy)
        c = fx*fx + fy*fy - entity.radius**2
        disc = b*b - 4*a*c
        if disc >= 0:
            self.hit_enemies.add(id(entity))
            return True
        return False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        ex, ey = cam.apply(self.ex, self.ey)
        alpha = self.life / self.duration
        w = max(1, int(self.width * alpha))
        c = (int(255*alpha), int(100*alpha), int(50*alpha))
        pygame.draw.line(surface, c, (int(sx), int(sy)), (int(ex), int(ey)), w)
        pygame.draw.line(surface, (255, 255, 255), (int(sx), int(sy)), (int(ex), int(ey)), max(1, w//3))