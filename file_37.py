import pygame
import math
import random
from settings import *
from enemies import Enemy

class BossPhase:
    def __init__(self, hp_threshold, speed_mult=1.0, damage_mult=1.0):
        self.hp_threshold = hp_threshold
        self.speed_mult = speed_mult
        self.damage_mult = damage_mult

class Boss(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.is_boss = True
        self.phase = 0
        self.phases = []
        self.vulnerable = True
        self.vulnerability_window = False
        self.vuln_timer = 0.0
        self.special_timer = 0.0
        self.enrage = False
        self.name = "Boss"
        self.attack_patterns = []
        self.current_pattern = 0
        self.pattern_timer = 0.0
        self.death_sequence = False
        self.death_timer = 0.0
        self.radius = 28

    def check_phase(self):
        for i, ph in enumerate(self.phases):
            if self.hp / self.max_hp <= ph.hp_threshold and self.phase <= i:
                self.phase = i + 1
                self.on_phase_change(i + 1)
                return True
        return False

    def on_phase_change(self, new_phase):
        self.vulnerable = False
        self.vuln_timer = 2.0
        self.effects.screen_shake(20, 0.8)
        self.effects.screen_flash((255, 50, 50), 0.5)
        for i in range(60):
            angle = random.uniform(0, math.pi * 2)
            self.particles.emit('explosion', self.pos[0] + math.cos(angle)*40,
                               self.pos[1] + math.sin(angle)*40, count=2)

    def update(self, dt, player, tilemap=None):
        if self.dead:
            if self.death_sequence:
                self.death_timer -= dt
                self.death_update(dt)
            return
        self.anim_timer += dt
        if self.anim_timer > 0.15:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self.update_dot(dt)
        if not self.vulnerable and self.vuln_timer > 0:
            self.vuln_timer -= dt
            if self.vuln_timer <= 0:
                self.vulnerable = True
        self.check_phase()
        self.ai_update(dt, player, tilemap)

    def take_damage(self, amount, dot_type=None):
        if not self.vulnerable