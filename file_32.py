import pygame
import math
import random
from projectiles import Projectile, FlameParticle
from constants import *
from utils import normalize, vec_from_angle
import assets

class WeaponBase:
    def __init__(self, name, fire_rate, ammo, max_ammo, reload_time):
        self.name = name
        self.fire_rate = fire_rate
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.reload_time = reload_time
        self._fire_timer = 0.0
        self._reload_timer = 0.0
        self.reloading = False

    def update(self, dt):
        if self._fire_timer > 0:
            self._fire_timer -= dt
        if self.reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self.ammo = self.max_ammo
                self.reloading = False

    def can_fire(self):
        return self._fire_timer <= 0 and not self.reloading and self.ammo > 0

    def start_reload(self):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self._reload_timer = self.reload_time

    def fire(self, x, y, angle, projectiles):
        raise NotImplementedError

    def get_info(self):
        return f"{self.name} {self.ammo}/{self.max_ammo}"

class Pistol(WeaponBase):
    def __init__(self):
        super().__init__("Pistol", fire_rate=0.18, ammo=15, max_ammo=15, reload_time=1.2)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        spd = 520
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 18, "player", "bullet", lifetime=1.5)
        projectiles.append(p)
        return [p]

class Shotgun(WeaponBase):
    def __init__(self):
        super().__init__("Shotgun", fire_rate=0.65, ammo=6, max_ammo=6, reload_time=1.8)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        new_projs = []
        for i in range(7):
            spread = random.uniform(-0.25, 0.25)
            a = angle + spread
            spd = random.uniform(380, 480)
            vx, vy = math.cos(a)*spd, math.sin(a)*spd
            p = Projectile(x, y, vx, vy, 14, "player", "pellet", lifetime=0.5)
            projectiles.append(p)
            new_projs.append(p)
        return new_projs

class Railgun(WeaponBase):
    def __init__(self):
        super().__init__("Railgun", fire_rate=1.2, ammo=5, max_ammo=5, reload_time=2.0)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        spd = 900
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 80, "player", "rail", pierce=True, lifetime=1.2)
        projectiles.append(p)
        return [p]

class GrenadeLauncher(WeaponBase):
    def __init__(self):
        super().__init__("Grenade Launcher", fire_rate=0.9, ammo=4, max_ammo=4, reload_time=2.2)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        spd = 280
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 55, "player", "grenade", aoe_radius=80, lifetime=1.8)
        projectiles.append(p)
        return [p]

class ChainLightning(WeaponBase):
    def __init__(self):
        super().__init__("Chain Lightning", fire_rate=0.5, ammo=8, max_ammo=8, reload_time=1.6)
        self.chain_range = 180
        self.chain_count = 4

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        spd = 450
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 28, "player", "lightning", lifetime=1.0)
        p.chain_remaining = self.chain_count
        p.chain_range = self.chain_range
        projectiles.append(p)
        return [p]

class Boomerang(WeaponBase):
    def __init__(self):
        super().__init__("Boomerang", fire_rate=1.0, ammo=1, max_ammo=1, reload_time=0.1)
        self._out = False

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire() or self._out:
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        self._out = True
        spd = 400
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 30, "player", "boomerang", pierce=True, lifetime=3.0)
        p._owner_ref = None
        p._return_x = x
        p._return_y = y
        p._time_out = 0.0
        p._boomerang_owner = self
        p.is_boomerang = True
        projectiles.append(p)
        return [p]

    def return_boomerang(self):
        self._out = False
        self.ammo = self.max_ammo

class Flamethrower(WeaponBase):
    def __init__(self):
        super().__init__("Flamethrower", fire_rate=0.05, ammo=60, max_ammo=60, reload_time=2.0)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        fp = FlameParticle(x, y, angle)
        fp.damage = 8
        fp.owner = "player"
        projectiles.append(fp)
        return [fp]

class Sniper(WeaponBase):
    def __init__(self):
        super().__init__("Sniper", fire_rate=1.5, ammo=3, max_ammo=3, reload_time=2.5)

    def fire(self, x, y, angle, projectiles):
        if not self.can_fire():
            return []
        self.ammo -= 1
        self._fire_timer = self.fire_rate
        spd = 1100
        vx, vy = math.cos(angle)*spd, math.sin(angle)*spd
        p = Projectile(x, y, vx, vy, 120, "player", "sniper", pierce=True, lifetime=1.0)
        projectiles.append(p)
        return [p]

WEAPON_CLASSES = [Pistol, Shotgun, Railgun, GrenadeLauncher, ChainLightning, Boomerang, Flamethrower, Sniper]

def make_weapon(idx):
    return WEAPON_CLASSES[idx % len(WEAPON_CLASSES)]()