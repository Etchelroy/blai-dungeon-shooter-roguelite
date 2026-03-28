import pygame
import math
import random
from constants import *
from utils import *
from projectiles import Projectile

class SecondaryAbility:
    def __init__(self, stype):
        self.stype = stype
        self.cooldown = 0.0
        self.active = False
        self.duration = 0.0
        self._configs = {
            SEC_SHIELD:    dict(cd=15.0, dur=4.0),
            SEC_TURRET:    dict(cd=20.0, dur=8.0),
            SEC_AIRSTRIKE: dict(cd=25.0, dur=0.0),
            SEC_FREEZE:    dict(cd=18.0, dur=3.0),
            SEC_VAMPIRIC:  dict(cd=12.0, dur=5.0),
            SEC_DECOY:     dict(cd=16.0, dur=6.0),
        }
        c = self._configs.get(stype, dict(cd=10.0, dur=0.0))
        self.max_cooldown = c['cd']
        self.max_duration = c['dur']

    def can_use(self):
        return self.cooldown <= 0

    def use(self):
        if not self.can_use():
            return False
        self.cooldown = self.max_cooldown
        self.active = True
        self.duration = self.max_duration
        return True

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.active:
            if self.max_duration > 0:
                self.duration -= dt
                if self.duration <= 0:
                    self.active = False
            else:
                self.active = False

class ShieldAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_SHIELD)
        self.radius = 40

    def draw(self, surface, px, py, cam_offset):
        if not self.active:
            return
        ox, oy = cam_offset
        sx, sy = int(px-ox), int(py-oy)
        alpha = int(180 * (self.duration / self.max_duration))
        shield_surf = pygame.Surface((self.radius*2+4, self.radius*2+4), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (80,150,255,alpha), (self.radius+2, self.radius+2), self.radius, 3)
        surface.blit(shield_surf, (sx-self.radius-2, sy-self.radius-2))

class TurretAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_TURRET)
        self.turret_x = 0
        self.turret_y = 0
        self.fire_timer = 0.0
        self.fire_rate = 0.5

    def use(self, x=0, y=0):
        if not self.can_use():
            return False
        self.cooldown = self.max_cooldown
        self.active = True
        self.duration = self.max_duration
        self.turret_x = x
        self.turret_y = y
        self.fire_timer = 0.0
        return True

    def update_turret(self, dt, enemies, proj_manager):
        if not self.active:
            return
        self.duration -= dt
        if self.duration <= 0:
            self.active = False
            return
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            best = None
            best_dist = 400
            for e in enemies:
                if not e.alive:
                    continue
                d = vec2_dist((self.turret_x, self.turret_y), (e.x, e.y))
                if d < best_dist:
                    best_dist = d
                    best = e
            if best:
                angle = angle_to((self.turret_x, self.turret_y), (best.x, best.y))
                vx = math.cos(angle)*500
                vy = math.sin(angle)*500
                proj_manager.add(Projectile(self.turret_x, self.turret_y, vx, vy, 15, 'bullet', 'player'))

    def draw(self, surface, cam_offset):
        if not self.active:
            return
        ox, oy = cam_offset
        sx, sy = int(self.turret_x-ox), int(self.turret_y-oy)
        pygame.draw.rect(surface, (80,80,80), (sx-10, sy-10, 20, 20))
        pygame.draw.rect(surface, CYAN, (sx-10, sy-10, 20, 20), 2)

class AirstrikeAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_AIRSTRIKE)
        self.strikes = []

    def use(self, target_x=0, target_y=0):
        if not self.can_use():
            return False
        self.cooldown = self.max_cooldown
        self.strikes = []
        for i in range(5):
            delay = i * 0.2
            ox = random.uniform(-80, 80)
            oy = random.uniform(-80, 80)
            self.strikes.append({'x': target_x+ox, 'y': target_y+oy, 'delay': delay, 'done': False})
        self.active = True
        return True

    def update_strikes(self, dt, enemies, particles, camera):
        if not self.active:
            return
        all_done = True
        for s in self.strikes:
            if s['done']:
                continue
            s['delay'] -= dt
            all_done = False
            if s['delay'] <= 0:
                s['done'] = True
                particles.emit_explosion(s['x'], s['y'], count=40)
                camera.add_shake(8)
                for e in enemies:
                    if not e.alive:
                        continue
                    if vec2_dist((s['x'], s['y']), (e.x, e.y)) < 80:
                        e.take_damage(45)
        if all_done:
            self.active = False

class FreezeAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_FREEZE)

    def use(self, enemies=None):
        if not self.can_use():
            return False
        self.cooldown = self.max_cooldown
        self.active = True
        self.duration = self.max_duration
        if enemies:
            for e in enemies:
                e.freeze(self.max_duration)
        return True

class VampiricAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_VAMPIRIC)
        self.lifesteal = 0.3

class DecoyAbility(SecondaryAbility):
    def __init__(self):
        super().__init__(SEC_DECOY)
        self.decoy_x = 0
        self.decoy_y = 0

    def use(self, x=0, y=0):
        if not self.can_use():
            return False
        self.cooldown = self.max_cooldown
        self.active = True
        self.duration = self.max_duration
        self.decoy_x = x + random.uniform(-100, 100)
        self.decoy_y = y + random.uniform(-100, 100)
        return True

    def draw(self, surface, cam_offset):
        if not self.active:
            return
        ox, oy = cam_offset
        sx, sy = int(self.decoy_x-ox), int(self.decoy_y-oy)
        pygame.draw.circle(surface, (80,180,255), (sx, sy), 14, 2)
        pygame.draw.circle(surface, (80,180,255,120), (sx, sy), 14)

def make_secondary(stype):
    if stype == SEC_SHIELD:    return ShieldAbility()
    if stype == SEC_TURRET:    return TurretAbility()
    if stype == SEC_AIRSTRIKE: return AirstrikeAbility()
    if stype == SEC_FREEZE:    return FreezeAbility()
    if stype == SEC_VAMPIRIC:  return VampiricAbility()
    if stype == SEC_DECOY:     return DecoyAbility()
    return SecondaryAbility(stype)