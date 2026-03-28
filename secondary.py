import pygame
import math
import random
from constants import *
from utils import angle_to, vec_from_angle, distance
from projectiles import Projectile
from particles import ParticleSystem

class SecondaryBase:
    def __init__(self, name, sec_id, cooldown):
        self.name = name; self.sec_id = sec_id
        self.cooldown = cooldown; self.timer = 0.0
        self.active = False; self.active_timer = 0.0

    def update(self, dt, player, enemies, projectiles, particles, camera):
        self.timer = max(0, self.timer - dt)

    def can_use(self):
        return self.timer <= 0

    def use(self, player, enemies, projectiles, particles, camera):
        pass

    @property
    def cooldown_fraction(self):
        return 1.0 - (self.timer / self.cooldown) if self.cooldown > 0 else 1.0

class Shield(SecondaryBase):
    def __init__(self):
        super().__init__("Shield", SEC_SHIELD, 8.0)
        self.shield_hp = 0; self.max_shield = 80
        self.duration = 4.0

    def use(self, player, enemies, projectiles, particles, camera):
        if not self.can_use(): return
        self.shield_hp = self.max_shield
        self.active = True
        self.active_timer = self.duration
        self.timer = self.cooldown
        particles.emit(player.x, player.y, CYAN, 15, speed=