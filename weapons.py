import pygame
import math
import random
from constants import *
from utils import angle_to, vec_from_angle
from projectiles import Projectile

class WeaponBase:
    def __init__(self, name, wpn_id, ammo, max_ammo, fire_rate, reload_time):
        self.name = name; self.wpn_id = wpn_id
        self.ammo = ammo; self.max_ammo = max_ammo
        self.fire_rate = fire_rate; self.reload_time = reload_time
        self.fire_timer = 0.0; self.reload_timer = 0.0
        self.is_reloading = False; self.auto = False

    def update(self, dt):
        self.fire_timer = max(0, self.fire_timer - dt)
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.ammo = self.max_ammo
                self.is_reloading = False

    def can_fire(self):
        return self.fire_timer <= 0 and not self.is_reloading and self.ammo > 0

    def start_reload(self):
        if not self.is_reloading and self.ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_timer = self.reload_time

    def consume_ammo(self, count=1):
        self.ammo -= count
        if self.ammo <= 0:
            self.ammo = 0
            self.start_reload()

    def fire(self, x, y, target_x, target_y, projectiles, particles):
        pass

class Pistol(WeaponBase):
    def __init__(self):
        super().__init__("Pistol", WPN_PISTOL, 12, 12, 0.25, 1.5)
        self.auto = False

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        vx, vy = math.cos(a)*600, math.sin(a)*600
        p = Projectile(x, y, vx, vy, 22, "player", "bullet", size=6, lifetime=2.0, color=YELLOW)
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        particles.emit_spark(x, y, YELLOW, 3)
        return True

class Shotgun(WeaponBase):
    def __init__(self):
        super().__init__("Shotgun", WPN_SHOTGUN, 6, 6, 0.7, 2.0)

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        for i in range(7):
            spread = random.uniform(-0.25, 0.25)
            ang = a + spread
            spd = random.uniform(350, 500)
            vx, vy = math.cos(ang)*spd, math.sin(ang)*spd
            p = Projectile(x, y, vx, vy, 18, "player", "pellet", size=5, lifetime=0.6, color=ORANGE)
            projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        particles.emit_spark(x, y, ORANGE, 8)
        return True

class Sniper(WeaponBase):
    def __init__(self):
        super().__init__("Sniper", WPN_SNIPER, 5, 5, 1.2, 2.5)

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        vx, vy = math.cos(a)*1200, math.sin(a)*1200
        p = Projectile(x, y, vx, vy, 90, "player", "sniper", pierce=True, size=5, lifetime=2.5, color=CYAN)
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        particles.emit_spark(x, y, CYAN, 10)
        return True

class SMG(WeaponBase):
    def __init__(self):
        super().__init__("SMG", WPN_SMG, 30, 30, 0.09, 2.0)
        self.auto = True

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty)) + random.uniform(-0.12, 0.12)
        spd = 520
        vx, vy = math.cos(a)*spd, math.sin(a)*spd
        p = Projectile(x, y, vx, vy, 14, "player", "bullet", size=4, lifetime=1.5, color=YELLOW)
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        return True

class RocketLauncher(WeaponBase):
    def __init__(self):
        super().__init__("Rocket", WPN_LAUNCHER, 3, 3, 0.8, 3.0)

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        spd = 380
        vx, vy = math.cos(a)*spd, math.sin(a)*spd
        p = Projectile(x, y, vx, vy, 60, "player", "rocket", size=10, lifetime=3.0, color=ORANGE)
        p.aoe_radius = 100; p.aoe_damage = 80
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        particles.emit_smoke(x, y, 4)
        return True

class ChainLightning(WeaponBase):
    def __init__(self):
        super().__init__("Chain", WPN_CHAIN, 20, 20, 0.35, 2.0)
        self.auto = True

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        vx, vy = math.cos(a)*500, math.sin(a)*500
        p = Projectile(x, y, vx, vy, 25, "player", "chain", size=7, lifetime=1.5, color=PURPLE)
        p.max_chain = 3
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        return True

class Boomerang(WeaponBase):
    def __init__(self):
        super().__init__("Boomerang", WPN_BOOMERANG, 1, 1, 1.5, 2.0)
        self._in_flight = False

    def update(self, dt):
        super().update(dt)

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty))
        spd = 420
        vx, vy = math.cos(a)*spd, math.sin(a)*spd
        p = Projectile(x, y, vx, vy, 40, "player", "boomerang", pierce=True, size=9, lifetime=4.0, color=TEAL)
        p.is_boomerang = True
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        return True

class Flamethrower(WeaponBase):
    def __init__(self):
        super().__init__("Flame", WPN_FLAMETHROWER, 100, 100, 0.06, 2.5)
        self.auto = True

    def fire(self, x, y, tx, ty, projectiles, particles):
        if not self.can_fire(): return False
        a = angle_to((x,y),(tx,ty)) + random.uniform(-0.3, 0.3)
        spd = random.uniform(200, 350)
        vx, vy = math.cos(a)*spd, math.sin(a)*spd
        p = Projectile(x, y, vx, vy, 8, "player", "flame", size=6, lifetime=0.5, color=RED)
        p.dot_damage = 5; p.dot_duration = 2.0
        projectiles.append(p)
        self.fire_timer = self.fire_rate
        self.consume_ammo()
        particles.emit(x, y, (255,140,20), 2, speed=60, life=0.3, size=8, gravity=-30)
        return True

WEAPON_CLASSES = [Pistol, Shotgun, Sniper, SMG, RocketLauncher, ChainLightning, Boomerang, Flamethrower]

def create_weapon(wpn_id):
    return WEAPON_CLASSES[wpn_id]()