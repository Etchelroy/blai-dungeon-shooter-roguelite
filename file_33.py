import pygame
import math
import random
from projectiles import Projectile
from utils import normalize, distance
from constants import *

class SecondaryBase:
    def __init__(self, name, cooldown):
        self.name = name
        self.cooldown = cooldown
        self._timer = 0.0
        self.active = False
        self.active_timer = 0.0

    def update(self, dt):
        if self._timer > 0:
            self._timer -= dt
        if self.active_timer > 0:
            self.active_timer -= dt
            if self.active_timer <= 0:
                self.active = False
                self.on_end()

    def ready(self):
        return self._timer <= 0

    def activate(self, player, enemies, projectiles, particles):
        if not self.ready():
            return False
        self._timer = self.cooldown
        return True

    def on_end(self):
        pass

    def cooldown_frac(self):
        return max(0.0, 1.0 - self._timer / self.cooldown)

class ShieldAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Shield", 8.0)
        self.duration = 3.0

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        player.shielded = True
        player.shield_timer = self.duration
        self.active = True
        self.active_timer = self.duration
        particles.emit(player.x, player.y, 20, (100,180,255), speed=80, life=0.5, size=8)
        return True

    def on_end(self):
        pass

class TimeSlowAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Time Slow", 12.0)
        self.duration = 4.0

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        self.active = True
        self.active_timer = self.duration
        for e in enemies:
            e.slow_timer = self.duration
            e.slow_factor = 0.25
        particles.emit(player.x, player.y, 15, (200,100,255), speed=60, life=0.8, size=6)
        return True

class NovaBombAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Nova Bomb", 15.0)

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        particles.emit_explosion(player.x, player.y, 60)
        radius = 200
        for e in enemies:
            d = distance((player.x, player.y), (e.x, e.y))
            if d < radius:
                e.take_damage(60, particles)
                nx, ny = normalize((e.x - player.x, e.y - player.y))
                e.vx += nx * 400
                e.vy += ny * 400
        for angle in range(0, 360, 20):
            a = math.radians(angle)
            spd = 350
            vx = math.cos(a) * spd
            vy = math.sin(a) * spd
            p = Projectile(player.x, player.y, vx, vy, 25, "player", "plasma", lifetime=1.0)
            projectiles.append(p)
        return True

class TurretAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Turret", 18.0)
        self.duration = 8.0
        self.turrets = []

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        self.active = True
        self.active_timer = self.duration
        for i in range(2):
            ox = random.uniform(-60, 60)
            oy = random.uniform(-60, 60)
            self.turrets.append(Turret(player.x + ox, player.y + oy, self.duration))
        particles.emit(player.x, player.y, 10, (255,200,50), speed=100, life=0.4)
        return True

    def update_turrets(self, dt, enemies, projectiles, particles):
        self.turrets = [t for t in self.turrets if t.alive]
        for t in self.turrets:
            t.update(dt, enemies, projectiles, particles)

    def on_end(self):
        self.turrets.clear()

    def draw_turrets(self, surface, cam):
        for t in self.turrets:
            t.draw(surface, cam)

class Turret:
    def __init__(self, x, y, lifetime):
        self.x = x; self.y = y
        self.alive = True
        self.lifetime = lifetime
        self._fire_timer = 0.0
        self.fire_rate = 0.4

    def update(self, dt, enemies, projectiles, particles):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self._fire_timer -= dt
        if self._fire_timer <= 0 and enemies:
            living = [e for e in enemies if e.alive]
            if living:
                target = min(living, key=lambda e: (e.x-self.x)**2+(e.y-self.y)**2)
                angle = math.atan2(target.y - self.y, target.x - self.x)
                vx = math.cos(angle)*400
                vy = math.sin(angle)*400
                p = Projectile(self.x, self.y, vx, vy, 20, "player", "bullet", lifetime=1.5)
                projectiles.append(p)
                self._fire_timer = self.fire_rate

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.circle(surface, (200,180,50), (sx, sy), 10)
        pygame.draw.circle(surface, (255,220,80), (sx, sy), 10, 2)

class TeleportAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Teleport", 6.0)

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        mx, my = pygame.mouse.get_pos()
        from camera import Camera
        wx, wy = player.x, player.y
        tx = player.x + (mx - 640)
        ty = player.y + (my - 360)
        particles.emit(player.x, player.y, 15, (180,100,255), speed=80, life=0.4)
        player.x = tx
        player.y = ty
        particles.emit(player.x, player.y, 15, (180,100,255), speed=80, life=0.4)
        return True

class AdrenalineAbility(SecondaryBase):
    def __init__(self):
        super().__init__("Adrenaline", 10.0)
        self.duration = 5.0

    def activate(self, player, enemies, projectiles, particles):
        if not super().activate(player, enemies, projectiles, particles):
            return False
        player.adrenaline_timer = self.duration
        self.active = True
        self.active_timer = self.duration
        particles.emit(player.x, player.y, 20, (255,80,80), speed=100, life=0.5, size=6)
        return True

SECONDARY_CLASSES = [ShieldAbility, TimeSlowAbility, NovaBombAbility, TurretAbility, TeleportAbility, AdrenalineAbility]

def make_secondary(idx):
    return SECONDARY_CLASSES[idx % len(SECONDARY_CLASSES)]()