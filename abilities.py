import pygame
import math
import random
from settings import *

class Ability:
    def __init__(self, ability_id):
        self.id = ability_id
        data = ABILITY_DEFS[ability_id]
        self.name = data['name']
        self.base_cooldown = data['cooldown']
        self.cooldown = 0.0
        self.duration = data.get('duration', 0.0)
        self.active_timer = 0.0
        self.active = False
        self.color = data.get('color', (200, 200, 255))

    def can_use(self):
        return self.cooldown <= 0

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.active:
            self.active_timer -= dt
            if self.active_timer <= 0:
                self.active = False

    def activate(self, player, enemies, projectiles, particles):
        if not self.can_use():
            return
        self.cooldown = self.base_cooldown
        if self.duration > 0:
            self.active = True
            self.active_timer = self.duration
        self._apply(player, enemies, projectiles, particles)

    def _apply(self, player, enemies, projectiles, particles):
        pass

    @property
    def cooldown_frac(self):
        return 1.0 - (self.cooldown / self.base_cooldown) if self.base_cooldown > 0 else 1.0


class ShieldAbility(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        player.shield = True
        player.shield_timer = self.duration

class NovaBurst(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        for e in enemies:
            d = math.hypot(e.x - player.x, e.y - player.y)
            if d < 200:
                e.take_damage(40)
                angle = math.atan2(e.y - player.y, e.x - player.x)
                e.vx += math.cos(angle) * 300
                e.vy += math.sin(angle) * 300
        for _ in range(40):
            a = random.random() * math.pi * 2
            particles.emit(player.x, player.y, math.cos(a) * random.uniform(100, 300),
                           math.sin(a) * random.uniform(100, 300), (255, 180, 60), random.uniform(0.3, 0.6), 4)

class TimeSlowAbility(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        player.time_slow = True
        player.time_slow_timer = self.duration

class TeleportAbility(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        mx, my = pygame.mouse.get_pos()
        from game import game_instance
        if game_instance:
            wx, wy = game_instance.camera.screen_to_world(mx, my)
            from tilemap import TILE_WALL, TILE_EMPTY
            col = int(wx // (TILE_SIZE * 3))
            row = int(wy // (TILE_SIZE * 3))
            if not game_instance.arena.tilemap.is_solid(col, row):
                for _ in range(20):
                    particles.emit(player.x, player.y, random.uniform(-150, 150),
                                   random.uniform(-150, 150), (150, 100, 255), 0.4, 5)
                player.x = wx
                player.y = wy
                for _ in range(20):
                    particles.emit(player.x, player.y, random.uniform(-150, 150),
                                   random.uniform(-150, 150), (150, 100, 255), 0.4, 5)

class MineDropAbility(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        from weapons import Projectile
        # Drop 3 mines around player
        for i in range(3):
            angle = (i / 3) * math.pi * 2
            mx2 = player.x + math.cos(angle) * 60
            my2 = player.y + math.sin(angle) * 60
            mine = Mine(mx2, my2, 80)
            projectiles.append(mine)

class AuraAbility(Ability):
    def _apply(self, player, enemies, projectiles, particles):
        player.damage_aura = True
        player.damage_aura_timer = self.duration

class Mine:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.radius = 10
        self.alive = True
        self.is_enemy = False
        self.timer = 8.0
        self.triggered = False
        self.explode_timer = 0.5

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def update(self, dt, tilemap):
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False
        if self.triggered:
            self.explode_timer -= dt
            if self.explode_timer <= 0:
                self.alive = False

    def trigger(self, enemies, particles):
        if self.triggered:
            return
        self.triggered = True
        for e in enemies:
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d < 100:
                e.take_damage(self.damage)
        for _ in range(30):
            a = random.random() * math.pi * 2
            particles.emit(self.x, self.y, math.cos(a) * random.uniform(100, 300),
                           math.sin(a) * random.uniform(100, 300), (255, 100, 20), 0.5, 6)

    def render(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        c = (255, 50, 50) if self.triggered else (200, 200, 50)
        pygame.draw.circle(screen, c, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), self.radius, 2)


ABILITY_DEFS = {
    'shield':    {'name': 'Shield',      'cooldown': 8.0,  'duration': 3.0,  'color': (100, 180, 255)},
    'nova':      {'name': 'Nova Burst',  'cooldown': 5.0,  'duration': 0.0,  'color': (255, 180, 60)},
    'timeslow':  {'name': 'Time Slow',   'cooldown': 12.0, 'duration': 4.0,  'color': (180, 100, 255)},
    'teleport':  {'name': 'Teleport',    'cooldown': 6.0,  'duration': 0.0,  'color': (150, 100, 255)},
    'mine':      {'name': 'Mine Drop',   'cooldown': 4.0,  'duration': 0.0,  'color': (255, 200, 50)},
    'aura':      {'name': 'Damage Aura', 'cooldown': 10.0, 'duration': 5.0,  'color': (255, 80, 80)},
}

def create_ability(ability_id):
    cls_map = {
        'shield': ShieldAbility,
        'nova': NovaBurst,
        'timeslow': TimeSlowAbility,
        'teleport': TeleportAbility,
        'mine': MineDropAbility,
        'aura': AuraAbility,
    }
    return cls_map[ability_id](ability_id)