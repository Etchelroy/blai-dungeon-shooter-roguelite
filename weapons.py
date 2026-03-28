import pygame
import math
import random
from projectiles import Projectile, BombProjectile, ReturnProjectile, LaserBeam

class Weapon:
    def __init__(self, name, ammo, max_ammo, fire_rate, damage):
        self.name = name
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.fire_rate = fire_rate
        self.fire_timer = 0
        self.damage = damage
        self.color = (255, 220, 0)

    def update(self):
        if self.fire_timer > 0:
            self.fire_timer -= 1

    def can_fire(self):
        return self.fire_timer <= 0 and self.ammo > 0

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        pass

    def get_info(self):
        return f"{self.name} {self.ammo}/{self.max_ammo}"

class Pistol(Weapon):
    def __init__(self):
        super().__init__("PISTOL", 999, 999, 12, 20)
        self.color = (255, 220, 80)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        speed = 12
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        projectiles.append(Projectile(x, y, vx, vy, self.damage, (255, 220, 80), 5, life=90))

class Shotgun(Weapon):
    def __init__(self):
        super().__init__("SHOTGUN", 40, 40, 30, 15)
        self.color = (255, 150, 50)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        for i in range(7):
            spread = math.radians(random.uniform(-20, 20))
            a = angle + spread
            speed = random.uniform(9, 13)
            vx = math.cos(a) * speed
            vy = math.sin(a) * speed
            p = Projectile(x, y, vx, vy, self.damage, (255, 150, 50), 4, life=50)
            projectiles.append(p)

class RifleWeapon(Weapon):
    def __init__(self):
        super().__init__("RIFLE", 90, 90, 6, 25)
        self.color = (100, 220, 255)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        speed = 18
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        p = Projectile(x, y, vx, vy, self.damage, (100, 220, 255), 4,
                       pierce=True, max_pierce=3, life=120)
        projectiles.append(p)

class RocketLauncher(Weapon):
    def __init__(self):
        super().__init__("ROCKETS", 12, 12, 50, 80)
        self.color = (255, 80, 30)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        speed = 9
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        p = BombProjectile(x, y, vx, vy, self.damage, aoe_radius=90)
        projectiles.append(p)

class ChainGun(Weapon):
    def __init__(self):
        super().__init__("CHAIN", 120, 120, 5, 18)
        self.color = (180, 255, 100)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        spread = math.radians(random.uniform(-5, 5))
        a = angle + spread
        speed = 14
        vx = math.cos(a) * speed
        vy = math.sin(a) * speed
        p = Projectile(x, y, vx, vy, self.damage, (180, 255, 100), 4,
                       chain=3, life=100)
        projectiles.append(p)

class Boomerang(Weapon):
    def __init__(self):
        super().__init__("BOOMERANG", 5, 5, 60, 35)
        self.active_boomerangs = 0
        self.color = (0, 220, 255)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can