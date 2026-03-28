import pygame
import math
import random
from constants import *
from utils import *
from projectiles import Projectile, FlameProjectile, BoomerangProjectile, ChainProjectile

class WeaponState:
    def __init__(self, wtype):
        self.wtype = wtype
        self.cooldown = 0.0
        self.ammo = -1  # -1 = infinite
        self.max_ammo = -1
        self.reload_time = 0.0
        self.reloading = False
        self._setup()

    def _setup(self):
        configs = {
            WEAPON_PISTOL:      dict(cooldown=0.25, ammo=-1),
            WEAPON_SHOTGUN:     dict(cooldown=0.7,  ammo=6, max_ammo=6, reload=1.2),
            WEAPON_RIFLE:       dict(cooldown=0.08, ammo=30, max_ammo=30, reload=1.5),
            WEAPON_LAUNCHER:    dict(cooldown=1.0,  ammo=4, max_ammo=4, reload=2.0),
            WEAPON_SNIPER:      dict(cooldown=1.2,  ammo=5, max_ammo=5, reload=2.0),
            WEAPON_FLAMETHROWER:dict(cooldown=0.05, ammo=100, max_ammo=100, reload=1.0),
            WEAPON_CHAIN:       dict(cooldown=0.4,  ammo=-1),
            WEAPON_BOOMERANG:   dict(cooldown=0.8,  ammo=-1),
        }
        c = configs.get(self.wtype, {})
        self.fire_cooldown = c.get('cooldown', 0.3)
        self.ammo = c.get('ammo', -1)
        self.max_ammo = c.get('max_ammo', -1)
        self.reload_duration = c.get('reload', 0.0)
        self.reloading = False
        self.reload_time = 0.0

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.reloading:
            self.reload_time -= dt
            if self.reload_time <= 0:
                self.reloading = False
                self.ammo = self.max_ammo

    def can_fire(self):
        return self.cooldown <= 0 and not self.reloading and (self.ammo != 0)

    def consume_ammo(self):
        if self.ammo > 0:
            self.ammo -= 1
            if self.ammo == 0 and self.max_ammo > 0:
                self.reloading = True
                self.reload_time = self.reload_duration

    def reload(self):
        if self.max_ammo > 0 and not self.reloading:
            self.reloading = True
            self.reload_time = self.reload_duration

def fire_weapon(wtype, px, py, angle, proj_manager, owner_ref=None, particles=None):
    speed_base = 500
    if wtype == WEAPON_PISTOL:
        vx = math.cos(angle)*speed_base
        vy = math.sin(angle)*speed_base
        proj_manager.add(Projectile(px, py, vx, vy, 20, 'bullet', 'player'))

    elif wtype == WEAPON_SHOTGUN:
        for i in range(7):
            spread = random.uniform(-0.25, 0.25)
            a = angle + spread
            spd = random.uniform(350, 500)
            vx = math.cos(a)*spd
            vy = math.sin(a)*spd
            proj_manager.add(Projectile(px, py, vx, vy, 15, 'pellet', 'player', size=7))

    elif wtype == WEAPON_RIFLE:
        spread = random.uniform(-0.03, 0.03)
        a = angle + spread
        vx = math.cos(a)*750
        vy = math.sin(a)*750
        proj_manager.add(Projectile(px, py, vx, vy, 18, 'bullet', 'player', pierce=1))

    elif wtype == WEAPON_LAUNCHER:
        vx = math.cos(angle)*300
        vy = math.sin(angle)*300
        p = Projectile(px, py, vx, vy, 60, 'rocket', 'player', aoe=100, size=12, lifetime=4.0)
        proj_manager.add(p)

    elif wtype == WEAPON_SNIPER:
        vx = math.cos(angle)*1200
        vy = math.sin(angle)*1200
        proj_manager.add(Projectile(px, py, vx, vy, 80, 'sniper', 'player', pierce=5, size=6, lifetime=2.0))

    elif wtype == WEAPON_FLAMETHROWER:
        spread = random.uniform(-0.3, 0.3)
        a = angle + spread
        spd = random.uniform(150, 280)
        vx = math.cos(a)*spd
        vy = math.sin(a)*spd
        proj_manager.add(FlameProjectile(px, py, vx, vy, 8))
        if particles:
            particles.emit(px, py, 2, (50,150), (255,100,0),
                          life_range=(0.1,0.3), size=5,
                          angle_range=(a-0.3, a+0.3))

    elif wtype == WEAPON_CHAIN:
        vx = math.cos(angle)*450
        vy = math.sin(angle)*450
        proj_manager.add(ChainProjectile(px, py, vx, vy, 25))

    elif wtype == WEAPON_BOOMERANG:
        vx = math.cos(angle)*380
        vy = math.sin(angle)*380
        proj_manager.add(BoomerangProjectile(px, py, vx, vy, 30, owner_ref))