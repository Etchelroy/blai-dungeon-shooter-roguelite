import pygame
import math
import random
from settings import *

class Enemy:
    def __init__(self, pos, particles, effects):
        self.pos = list(pos)
        self.vel = [0.0, 0.0]
        self.particles = particles
        self.effects = effects
        self.hp = 50
        self.max_hp = 50
        self.radius = 14
        self.speed = 80
        self.damage = 10
        self.color = (200, 50, 50)
        self.dead = False
        self.death_handled = False
        self.score_value = 10
        self.coin_value = 1
        self.tier = 1
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.hit_flash = 0.0
        self.ai_timer = 0.0
        self.name = "Enemy"
        self.bullets = []
        self.facing = 0.0
        self.dot_stacks = {}

    def take_damage(self, amount, dot_type=None):
        if self.dead:
            return
        if dot_type:
            self.dot_stacks[dot_type] = {'damage': amount * 0.1, 'timer': 3.0, 'tick': 0.5, 'tick_timer': 0}
            return
        self.hp -= amount
        self.hit_flash = 0.15
        if self.hp <= 0:
            self.die()

    def die(self):
        self.dead = True
        self.spawn_death_particles()

    def spawn_death_particles(self):
        for i in range(20):
            angle = random.uniform(0, math.pi * 2)
            self.particles.emit('explosion', self.pos[0], self.pos[1], count=1,
                               color=self.color)
        for i in range(8):
            self.particles.emit('spark', self.pos[0], self.pos[1], count=1,
                               color=(255, 200, 100))

    def update_dot(self, dt):
        to_remove = []
        for dot_type, data in self.dot_stacks.items():
            data['timer'] -= dt
            data['tick_timer'] -= dt
            if data['tick_timer'] <= 0:
                data['tick_timer'] = data['tick']
                self.hp -= data['damage']
                self.hit_flash = 0.05
                if self.hp <= 0:
                    self.die()
            if data['timer'] <= 0:
                to_remove.append(dot_type)
        for k in to_remove:
            del self.dot_stacks[k]

    def move_toward_player(self, player_pos, dt, tilemap=None):
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.facing = math.atan2(dy, dx)
            nx = dx / dist
            ny = dy / dist
            new_x = self.pos[0] + nx * self.speed * dt
            new_y = self.pos[1] + ny * self.speed * dt
            if tilemap and tilemap.is_wall(new_x, self.pos[1], self.radius):
                new_x = self.pos[0]
            if tilemap and tilemap.is_wall(self.pos[0], new_y, self.radius):
                new_y = self.pos[1]
            self.pos[0] = new_x
            self.pos[1] = new_y

    def update(self, dt, player, tilemap=None):
        if self.dead:
            return
        self.anim_timer += dt
        if self.anim_timer > 0.2:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self.update_dot(dt)
        self.ai_update(dt, player, tilemap)

    def ai_update(self, dt, player, tilemap):
        self.move_toward_player(player.pos, dt, tilemap)

    def draw(self, surface, camera):
        sx = int(self.pos[0] - camera.x)
        sy = int(self.pos[1] - camera.y)
        color = (255, 255, 255) if self.hit_flash > 0 else self.color
        pygame.draw.circle(surface, (20, 20, 20), (sx, sy + 3), self.radius)
        pygame.draw.circle(surface, color, (sx, sy), self.radius)
        pygame.draw.circle(surface, tuple(min(255, c + 60) for c in color), (sx, sy), self.radius, 2)
        eye_x = sx + int(math.cos(self.facing) * self.radius * 0.5)
        eye_y = sy + int(math.sin(self.facing) * self.radius * 0.5)
        pygame.draw.circle(surface, (255, 255, 50), (eye_x, eye_y), 3)
        hp_ratio = self.hp / self.max_hp
        bar_w = self.radius * 2
        bar_x = sx - self.radius
        bar_y = sy - self.radius - 8
        pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, 4))
        pygame.draw.rect(surface, (220, 50, 50), (bar_x, bar_y, int(bar_w * hp_ratio), 4))
        for dot_type, data in self.dot_stacks.items():
            dot_colors = {'fire': (255, 100, 0), 'poison': (0, 200, 50), 'ice': (100, 200, 255)}
            dc = dot_colors.get(dot_type, (200, 200, 200))
            pygame.draw.circle(surface, dc, (sx, sy), self.radius + 3, 2)


class Grunt(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Grunt"
        self.hp = self.max_hp = 40
        self.speed = 90
        self.damage = 10
        self.color = (180, 60, 60)
        self.score_value = 10
        self.radius = 12


class Archer(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Archer"
        self.hp = self.max_hp = 30
        self.speed = 60
        self.damage = 15
        self.color = (200, 120, 50)
        self.score_value = 20
        self.shoot_timer = 0.0
        self.shoot_cooldown = 2.0
        self.preferred_dist = 200
        self.radius = 11

    def ai_update(self, dt, player, tilemap):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.facing = math.atan2(dy, dx)
        if dist > self.preferred_dist + 30:
            self.move_toward_player(player.pos, dt, tilemap)
        elif dist < self.preferred_dist - 30:
            nx = -dx/dist
            ny = -dy/dist
            self.pos[0] += nx * self.speed * 0.5 * dt
            self.pos[1] += ny * self.speed * 0.5 * dt
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and dist < 350:
            self.shoot_timer = self.shoot_cooldown
            if dist > 0:
                self.bullets.append({
                    'pos': self.pos[:],
                    'vel': [dx/dist * 250, dy/dist * 250],
                    'damage': self.damage,
                    'radius': 5,
                    'life': 2.0,
                    'color': (255, 150, 50)
                })


class Charger(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Charger"
        self.hp = self.max_hp = 80
        self.speed = 60
        self.damage = 25
        self.color = (150, 50, 200)
        self.score_value = 30
        self.radius = 16
        self.charge_speed = 350
        self.charging = False
        self.charge_timer = 0.0
        self.charge_dir = [0, 0]
        self.charge_cooldown = 3.0
        self.ai_timer = random.uniform(1, 2)

    def ai_update(self, dt, player, tilemap):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if self.charging:
            self.pos[0] += self.charge_dir[0] * self.charge_speed * dt
            self.pos[1] += self.charge_dir[1] * self.charge_speed * dt
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.charging = False
                self.ai_timer = self.charge_cooldown
        else:
            self.ai_timer -= dt
            self.move_toward_player(player.pos, dt, tilemap)
            if self.ai_timer <= 0 and dist < 300:
                self.charging = True
                self.charge_timer = 0.4
                if dist > 0:
                    self.charge_dir = [dx/dist, dy/dist]
                self.particles.emit('spark', self.pos[0], self.pos[1], count=10, color=(150, 50, 200))


class Shielder(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Shielder"
        self.hp = self.max_hp = 120
        self.speed = 50
        self.damage = 15
        self.color = (80, 120, 200)
        self.score_value = 40
        self.radius = 16
        self.shield_hp = 60
        self.shield_angle = 0.0

    def take_damage(self, amount, dot_type=None):
        if self.dead:
            return
        if self.shield_hp > 0:
            self.shield_hp -= amount * 0.5
            self.hit_flash = 0.1
            return
        super().take_damage(amount, dot_type)

    def update(self, dt, player, tilemap=None):
        self.shield_angle += dt * 2
        super().update(dt, player, tilemap)

    def draw(self, surface, camera):
        super().draw(surface, camera)
        if self.shield_hp > 0:
            sx = int(self.pos[0] - camera.x)
            sy = int(self.pos[1] - camera.y)
            shield_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            ratio = self.shield_hp / 60
            alpha = int(100 * ratio)
            pygame.draw.circle(shield_surf, (100, 150, 255, alpha), (30, 30), 28, 4)
            surface.blit(shield_surf, (sx - 30, sy - 30))


class Summoner(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Summoner"
        self.hp = self.max_hp = 60
        self.speed = 40
        self.damage = 0
        self.color = (200, 50, 200)
        self.score_value = 50
        self.radius = 14
        self.summon_timer = 0.0
        self.summon_cooldown = 5.0
        self.summon_count = 0
        self.max_summons = 3
        self.spawn_queue = []

    def ai_update(self, dt, player, tilemap):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 300:
            self.move_toward_player(player.pos, dt * 0.3, tilemap)
        else:
            self.move_toward_player(player.pos, dt, tilemap)
        self.summon_timer -= dt
        if self.summon_timer <= 0 and self.summon_count < self.max_summons:
            self.summon_timer = self.summon_cooldown
            angle = random.uniform(0, math.pi * 2)
            spawn_x = self.pos[0] + math.cos(angle) * 60
            spawn_y = self.pos[1] + math.sin(angle) * 60
            self.spawn_queue.append((spawn_x, spawn_y))
            self.particles.emit('spark', self.pos[0], self.pos[1], count=15, color=(200, 50, 200))


class Exploder(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Exploder"
        self.hp = self.max_hp = 35
        self.speed = 110
        self.damage = 50
        self.color = (255, 150, 0)
        self.score_value = 25
        self.radius = 14
        self.explode_range = 80
        self.fuse_timer = None
        self.fuse_duration = 1.5

    def ai_update(self, dt, player, tilemap):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < self.explode_range:
            if self.fuse_timer is None:
                self.fuse_timer = self.fuse_duration
        if self.fuse_timer is not None:
            self.fuse_timer -= dt
            self.color = (255, int(150 * (self.fuse_timer / self.fuse_duration)), 0)
            if self.fuse_timer <= 0:
                self.explode(player)
                return
        else:
            self.move_toward_player(player.pos, dt, tilemap)

    def explode(self, player):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        if math.sqrt(dx*dx + dy*dy) < self.explode_range:
            player.take_damage(self.damage)
        for i in range(40):
            angle = random.uniform(0, math.pi * 2)
            self.particles.emit('explosion', self.pos[0] + math.cos(angle)*20,
                               self.pos[1] + math.sin(angle)*20, count=2)
        self.effects.screen_shake(15, 0.4)
        self.die()


class Ghost(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Ghost"
        self.hp = self.max_hp = 50
        self.speed = 70
        self.damage = 12
        self.color = (180, 200, 255)
        self.score_value = 35
        self.radius = 13
        self.phase_timer = 0.0
        self.phase_duration = 2.0
        self.phased = False
        self.alpha = 255

    def take_damage(self, amount, dot_type=None):
        if self.phased:
            return
        super().take_damage(amount, dot_type)

    def ai_update(self, dt, player, tilemap):
        self.phase_timer -= dt
        if self.phase_timer <= 0:
            self.phased = not self.phased
            self.phase_timer = self.phase_duration
        self.move_toward_player(player.pos, dt)

    def draw(self, surface, camera):
        sx = int(self.pos[0] - camera.x)
        sy = int(self.pos[1] - camera.y)
        alpha = 80 if self.phased else 200
        ghost_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        color = self.color if not self.hit_flash else (255, 255, 255)
        pygame.draw.circle(ghost_surf, (*color, alpha), (20, 20), self.radius)
        surface.blit(ghost_surf, (sx - 20, sy - 20))
        if not self.phased:
            hp_ratio = self.hp / self.max_hp
            bar_w = self.radius * 2
            pygame.draw.rect(surface, (80, 0, 0), (sx - self.radius, sy - self.radius - 8, bar_w, 4))
            pygame.draw.rect(surface, (220, 50, 50), (sx - self.radius, sy - self.radius - 8, int(bar_w * hp_ratio), 4))


class Sniper(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Sniper"
        self.hp = self.max_hp = 45
        self.speed = 40
        self.damage = 35
        self.color = (200, 200, 50)
        self.score_value = 45
        self.radius = 11
        self.shoot_timer = 0.0
        self.charge_timer = 0.0
        self.charge_duration = 1.5
        self.charging = False
        self.shoot_cooldown = 4.0
        self.target_pos = None

    def ai_update(self, dt, player, tilemap):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.facing = math.atan2(dy, dx)
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and not self.charging:
            self.charging = True
            self.charge_timer = self.charge_duration
            self.target_pos = player.pos[:]
            self.particles.emit('spark', self.pos[0], self.pos[1], count=5, color=(255, 255, 0))
        if self.charging:
            self.charge_timer -= dt
            pct = 1 - (self.charge_timer / self.charge_duration)
            if self.charge_timer <= 0:
                self.charging = False
                self.shoot_timer = self.shoot_cooldown
                if self.target_pos:
                    tdx = self.target_pos[0] - self.pos[0]
                    tdy = self.target_pos[1] - self.pos[1]
                    td = math.sqrt(tdx**2 + tdy**2)
                    if td > 0:
                        self.bullets.append({
                            'pos': self.pos[:],
                            'vel': [tdx/td * 500, tdy/td * 500],
                            'damage': self.damage,
                            'radius': 6,
                            'life': 2.0,
                            'color': (255, 255, 0),
                            'pierces': 3
                        })
        if dist < 400:
            self.move_toward_player(player.pos, dt * (-0.5 if dist < 200 else 0.3), tilemap)


class Tank(Enemy):
    def __init__(self, pos, particles, effects):
        super().__init__(pos, particles, effects)
        self.name = "Tank"
        self.hp = self.max_hp = 250
        self.speed = 45
        self.damage = 30
        self.color = (100, 100, 100)
        self.score_value = 80
        self.radius = 22
        self.tier = 2
        self.stomp_timer = 0.0
        self.stomp_cooldown = 3.0

    def ai_update(self, dt, player, tilemap):
        self.stomp_timer -= dt
        if self.stomp_timer <= 0:
            self.stomp_timer = self.stomp_cooldown
            self.effects.screen_shake(5, 0.2)
            self.particles.emit('dust', self.pos[0], self.pos[1], count=20)
        self.move_toward_player(player.pos, dt, tilemap)


ENEMY_TYPES = {
    'grunt': Grunt,
    'archer': Archer,
    'charger': Charger,
    'shielder': Shielder,
    'summoner': Summoner,
    'exploder': Exploder,
    'ghost': Ghost,
    'sniper': Sniper,
    'tank': Tank,
}

TIER_ENEMIES = {
    1: ['grunt', 'archer', 'exploder'],
    2: ['charger', 'shielder', 'ghost', 'sniper'],
    3: ['summoner', 'tank'],
}

def create_enemy(etype, pos, particles, effects):
    cls = ENEMY_TYPES.get(etype, Grunt)
    return cls(pos, particles, effects)

def get_wave_enemies(wave):
    if wave <= 3:
        pool = TIER_ENEMIES[1]
    elif wave <= 7:
        pool = TIER_ENEMIES[1] + TIER_ENEMIES[2]
    else:
        pool = TIER_ENEMIES[1] + TIER_ENEMIES[2] + TIER_ENEMIES[3]
    count = min(5 + wave * 2, 25)
    return [(random.choice(pool), count)]