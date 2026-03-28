import pygame
import math
import random
from constants import *
from utils import normalize, distance, angle_to, vec_from_angle

class Projectile:
    def __init__(self, x, y, vx, vy, damage, owner="player", proj_type="bullet",
                 pierce=False, size=8, lifetime=3.0, color=YELLOW):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.damage = damage; self.owner = owner; self.proj_type = proj_type
        self.pierce = pierce; self.size = size; self.lifetime = lifetime
        self.color = color; self.alive = True
        self.hit_enemies = set()
        self.homing = False; self.homing_strength = 0
        self.homing_target = None
        self.chain_count = 0; self.max_chain = 0
        self.is_boomerang = False; self.return_phase = False
        self.origin_x = x; self.origin_y = y
        self.aoe_radius = 0; self.aoe_damage = 0
        self.dot_damage = 0; self.dot_duration = 0

    def update(self, dt, walls, enemies, player, particles):
        if not self.alive:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            if self.aoe_radius > 0:
                self._explode(enemies, particles)
            self.alive = False
            return

        if self.homing and self.homing_target and self.homing_target.alive:
            tx, ty = self.homing_target.x, self.homing_target.y
            desired_angle = angle_to((self.x, self.y), (tx, ty))
            current_angle = math.atan2(self.vy, self.vx)
            diff = desired_angle - current_angle
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            current_angle += diff * min(1.0, self.homing_strength * dt)
            spd = math.hypot(self.vx, self.vy)
            self.vx = math.cos(current_angle) * spd
            self.vy = math.sin(current_angle) * spd

        if self.is_boomerang:
            d = distance((self.x, self.y), (self.origin_x, self.origin_y))
            if not self.return_phase and d > 280:
                self.return_phase = True
            if self.return_phase:
                if self.owner == "player":
                    tx, ty = player.x, player.y
                else:
                    tx, ty = self.origin_x, self.origin_y
                a = angle_to((self.x, self.y), (tx, ty))
                spd = math.hypot(self.vx, self.vy)
                self.vx = math.cos(a) * spd
                self.vy = math.sin(a) * spd
                if distance((self.x, self.y), (tx, ty)) < 20:
                    self.alive = False
                    return

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Wall collision
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        if walls and 0 <= tile_x < len(walls[0]) and 0 <= tile_y < len(walls):
            if walls[tile_y][tile_x] == TILE_WALL or walls[tile_y][tile_x] == TILE_WALL_ALT:
                if self.aoe_radius > 0:
                    self._explode(enemies, particles)
                particles.emit_spark(self.x, self.y, self.color, 5)
                self.alive = False
                return

        # Enemy/player collision
        if self.owner == "player":
            for enemy in enemies:
                if not enemy.alive or id(enemy) in self.hit_enemies:
                    continue
                if distance((self.x, self.y), (enemy.x, enemy.y)) < self.size + enemy.radius:
                    self.hit_enemies.add(id(enemy))
                    enemy.take_damage(self.damage, particles)
                    if self.dot_damage > 0:
                        enemy.apply_dot(self.dot_damage, self.dot_duration)
                    if self.max_chain > 0 and self.chain_count < self.max_chain:
                        self._do_chain(enemy, enemies, particles)
                    if self.aoe_radius > 0:
                        self._explode(enemies, particles)
                        self.alive = False
                        return
                    if not self.pierce:
                        self.alive = False
                        return
        elif self.owner == "enemy":
            if distance((self.x, self.y), (player.x, player.y)) < self.size + 16:
                if not player.is_invincible():
                    player.take_damage(self.damage, particles)
                    particles.emit_blood(player.x, player.y, 5)
                self.alive = False

    def _explode(self, enemies, particles):
        particles.emit_explosion(self.x, self.y, self.aoe_radius)
        for enemy in enemies:
            if not enemy.alive:
                continue
            d = distance((self.x, self.y), (enemy.x, enemy.y))
            if d < self.aoe_radius:
                dmg = int(self.aoe_damage * (1 - d / self.aoe_radius))
                enemy.take_damage(max(10, dmg), particles)

    def _do_chain(self, hit_enemy, enemies, particles):
        best = None
        best_d = float('inf')
        for e in enemies:
            if not e.alive or e is hit_enemy or id(e) in self.hit_enemies:
                continue
            d = distance((hit_enemy.x, hit_enemy.y), (e.x, e.y))
            if d < 200 and d < best_d:
                best_d = d; best = e
        if best:
            particles.emit_chain(hit_enemy.x, hit_enemy.y, best.x, best.y)
            self.hit_enemies.add(id(best))
            best.take_damage(self.damage * 0.7, particles)
            self.chain_count += 1

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if -20 < sx < SCREEN_WIDTH+20 and -20 < sy < SCREEN_HEIGHT+20:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.size)
            inner_c = tuple(min(255, c+80) for c in self.color[:3])
            pygame.draw.circle(surface, inner_c, (int(sx), int(sy)), max(1, self.size-2))