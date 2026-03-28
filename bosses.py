import pygame
import math
import random
from particles import Particle

class BossProjectile:
    def __init__(self, x, y, vx, vy, color, radius, damage, lifetime=4.0):
        self.pos = [x, y]
        self.vel = [vx, vy]
        self.color = color
        self.radius = radius
        self.damage = damage
        self.lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.pos[0], self.pos[1])
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
        inner = tuple(min(255, c+80) for c in self.color)
        pygame.draw.circle(surface, inner, (int(sx), int(sy)), max(1, self.radius-3))

    def get_rect(self):
        return pygame.Rect(self.pos[0]-self.radius, self.pos[1]-self.radius,
                          self.radius*2, self.radius*2)


class Boss:
    def __init__(self, x, y, name, max_hp, phase_thresholds):
        self.pos = [float(x), float(y)]
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.phase = 1
        self.phase_thresholds = phase_thresholds  # e.g. [0.66, 0.33]
        self.projectiles = []
        self.alive = True
        self.death_timer = 0
        self.dying = False
        self.invuln = False
        self.invuln_timer = 0
        self.attack_timer = 0
        self.move_timer = 0
        self.target_pos = [x, y]
        self.speed = 80
        self.iframes = 0
        self.radius = 40
        self.phase_transition_timer = 0
        self.phase_transitioning = False
        self.anim_timer = 0
        self.enrage = False

    def take_damage(self, dmg):
        if self.invuln or self.iframes > 0 or self.phase_transitioning:
            return False
        self.hp -= dmg
        self.iframes = 0.1
        if self.hp <= 0:
            self.hp = 0
            if not self.dying:
                self.dying = True
            return True
        return False

    def check_phase(self):
        ratio = self.hp / self.max_hp
        new_phase = 1
        for i, threshold in enumerate(self.phase_thresholds):
            if ratio <= threshold:
                new_phase = i + 2
        if new_phase > self.phase and not self.phase_transitioning:
            self.phase = new_phase
            self.phase_transitioning = True
            self.phase_transition_timer = 2.0
            self.invuln = True
            return True
        return False

    def update_base(self, dt, player, particles):
        self.anim_timer += dt
        if self.iframes > 0:
            self.iframes -= dt
        if self.phase_transitioning:
            self.phase_transition_timer -= dt
            # Explosion particles
            if random.random() < 0.3:
                angle = random.uniform(0, math.pi*2)
                speed = random.uniform(50, 150)
                p = Particle(self.pos[0], self.pos[1],
                            math.cos