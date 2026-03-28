import pygame
import math
import random
from constants import *
from utils import *
from assets import get_player_surf, get_font
from weapons import WeaponState, fire_weapon
from secondary import make_secondary

class Player:
    def __init__(self, x, y, proj_manager, particles):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 14
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.alive = True

        self.proj_manager = proj_manager
        self.particles = particles

        self.weapon_index = 0
        self.weapons = [WeaponState(i) for i in range(8)]
        self.current_weapon = self.weapons[self.weapon_index]

        self.secondary_index = 0
        self.secondary = make_secondary(SEC_SHIELD)

        self.dash_cooldown = 0.0
        self.dash_timer = 0.0
        self.dashing = False
        self.iframe_timer = 0.0
        self.dash_angle = 0.0
        self.afterimage_timer = 0.0

        self.melee_cooldown = 0.0
        self.melee_active = False
        self.melee_timer = 0.0
        self.melee_angle = 0.0

        self.aim_angle = 0.0
        self.score = 0
        self.coins = 0
        self.combo = 0
# filename: enemies.py
import pygame
import math
import random
from constants import *
from particles import ParticleSystem

class BaseEnemy:
    def __init__(self, x, y, hp, speed, damage, score_value, coin_value):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.score_value = score_value
        self.coin_value = coin_value
        self.vx = 0
        self.vy = 0
        self.alive = True
        self.radius = 16
        self.color = (180, 60, 60)
        self.stun_timer = 0
        self.poison_timer = 0
        self.poison_damage = 0
        self.burn_timer = 0
        self.burn_damage = 0
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.knockback_x = 0
        self.knockback_y = 0
        self.death_particles_spawned = False
        self.flash_timer = 0
        self.target_x = x
        self.target_y = y
        self.tier = 1
        self.name = "Enemy"

    def apply_status(self, status, duration, value=0):
        if status == "stun":
            self.stun_timer = max(self.stun_timer, duration)
        elif status == "poison":
            self.poison_timer = max(self.poison_timer, duration)
            self.poison_damage = max(self.poison_damage, value)
        elif status == "burn":
            self.burn_timer = max(self.burn_timer, duration)
            self.burn_damage = max(self.burn_damage, value)
        elif status == "slow":
            self.slow_timer = max(self.slow_timer, duration)
            self.slow_factor = min(self.slow_factor, value)

    def take_damage(self, amount, kx=0, ky=0):
        self.hp -= amount
        self.flash_timer = 0.1
        self.knockback_x += kx * 200
        self.knockback_y += ky * 200
        if self.hp <= 0:
            self.alive = False

    def update_status_effects(self, dt):
        if self.stun_timer > 0:
            self.stun_timer -= dt
        if self.poison_timer > 0:
            self.poison_timer -= dt
            self.take_damage(self.poison_damage * dt)
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.take_damage(self.burn_damage * dt)
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.knockback_x *= (1 - 10 * dt)
        self.knockback_y *= (1 - 10 * dt)

    def move_toward_player(self, px, py, dt, walls=None):
        if self.stun_timer > 0:
            return
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            spd = self.speed * self.slow_factor
            self.vx = (dx / dist) * spd
            self.vy = (dy / dist) * spd
        self.x += (self.vx + self.knockback_x) * dt
        self.y += (self.vy + self.knockback_y) * dt

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surface, color, (int(sx), int(sy)), self.radius)
        bar_w = self.radius * 2
        bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (80, 0, 0), (int(sx) - self.radius, int(sy) - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surface, (0, 220, 0), (int(sx) - self.radius, int(sy) - self.radius - 8, int(bar_w * ratio), bar_h))

    def spawn_death_particles(self, particle_system):
        if not self.death_particles_spawned:
            self.death_particles_spawned = True
            for _ in range(20):
                angle = random.uniform(0, math.pi * 2)
                spd = random.uniform(50, 200)
                particle_system.spawn(self.x, self.y,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    self.color, random.uniform(0.3, 0.8), random.uniform(3, 8))


class Grunt(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=40, speed=80, damage=10, score_value=100, coin_value=2)
        self.color = (180, 60, 60)
        self.radius = 14
        self.name = "Grunt"
        self.tier = 1


class Speeder(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=25, speed=150, damage=8, score_value=150, coin_value=2)
        self.color = (255, 140, 0)
        self.radius = 10
        self.name = "Speeder"
        self.tier = 1
        self.zigzag_timer = 0
        self.zigzag_dir = 1

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        if self.stun_timer > 0:
            return
        self.zigzag_timer += dt
        if self.zigzag_timer > 0.4:
            self.zigzag_timer = 0
            self.zigzag_dir *= -1
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            perp_x = -dy / dist * self.zigzag_dir * 60
            perp_y = dx / dist * self.zigzag_dir * 60
            spd = self.speed * self.slow_factor
            self.vx = (dx / dist) * spd + perp_x
            self.vy = (dy / dist) * spd + perp_y
        self.x += (self.vx + self.knockback_x) * dt
        self.y += (self.vy + self.knockback_y) * dt


class Brute(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=150, speed=50, damage=25, score_value=300, coin_value=5)
        self.color = (120, 40, 140)
        self.radius = 22
        self.name = "Brute"
        self.tier = 2
        self.charge_cooldown = 3.0
        self.charge_timer = 0
        self.charging = False
        self.charge_vx = 0
        self.charge_vy = 0
        self.charge_duration = 0

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        if self.stun_timer > 0:
            return
        self.charge_cooldown -= dt
        if self.charging:
            self.charge_duration -= dt
            self.x += self.charge_vx * dt
            self.y += self.charge_vy * dt
            if self.charge_duration <= 0:
                self.charging = False
        else:
            self.move_toward_player(player.x, player.y, dt, walls)
            if self.charge_cooldown <= 0:
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.hypot(dx, dy)
                if dist < 300 and dist > 0:
                    self.charge_cooldown = 3.0
                    self.charging = True
                    self.charge_duration = 0.4
                    self.charge_vx = (dx / dist) * 400
                    self.charge_vy = (dy / dist) * 400
                    for _ in range(10):
                        particle_system.spawn(self.x, self.y,
                            random.uniform(-50, 50), random.uniform(-50, 50),
                            (200, 100, 255), 0.3, 5)


class Shooter(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=60, speed=40, damage=12, score_value=250, coin_value=4)
        self.color = (60, 120, 200)
        self.radius = 14
        self.name = "Shooter"
        self.tier = 2
        self.shoot_cooldown = 2.0
        self.shoot_timer = 0
        self.preferred_dist = 200
        self.projectiles = []

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        if self.stun_timer > 0:
            return
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.preferred_dist + 20:
            spd = self.speed * self.slow_factor
            if dist > 0:
                self.x += (dx / dist) * spd * dt
                self.y += (dy / dist) * spd * dt
        elif dist < self.preferred_dist - 20:
            spd = self.speed * self.slow_factor
            if dist > 0:
                self.x -= (dx / dist) * spd * dt
                self.y -= (dy / dist) * spd * dt
        self.x += self.knockback_x * dt
        self.y += self.knockback_y * dt
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown and dist < 400:
            self.shoot_timer = 0
            if dist > 0:
                self.projectiles.append({
                    'x': self.x, 'y': self.y,
                    'vx': (dx / dist) * 200,
                    'vy': (dy / dist) * 200,
                    'damage': self.damage,
                    'lifetime': 3.0,
                    'radius': 6,
                    'color': (100, 160, 255)
                })

    def draw(self, surface, camera):
        super().draw(surface, camera)
        for proj in self.projectiles:
            sx, sy = camera.world_to_screen(proj['x'], proj['y'])
            pygame.draw.circle(surface, proj['color'], (int(sx), int(sy)), proj['radius'])

    def update_projectiles(self, dt, player):
        hits = []
        alive = []
        for proj in self.projectiles:
            proj['x'] += proj['vx'] * dt
            proj['y'] += proj['vy'] * dt
            proj['lifetime'] -= dt
            dx = proj['x'] - player.x
            dy = proj['y'] - player.y
            if math.hypot(dx, dy) < player.radius + proj['radius']:
                hits.append(proj)
                player.take_damage(proj['damage'])
            elif proj['lifetime'] > 0:
                alive.append(proj)
        self.projectiles = alive
        return hits


class Shielder(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=80, speed=55, damage=15, score_value=350, coin_value=5)
        self.color = (80, 200, 80)
        self.radius = 16
        self.name = "Shielder"
        self.tier = 2
        self.shield_hp = 60
        self.shield_max = 60
        self.shield_active = True
        self.shield_regen_timer = 0

    def take_damage(self, amount, kx=0, ky=0):
        if self.shield_active and self.shield_hp > 0:
            self.shield_hp -= amount
            self.flash_timer = 0.1
            if self.shield_hp <= 0:
                self.shield_active = False
                self.shield_hp = 0
        else:
            super().take_damage(amount, kx, ky)

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)
        if not self.shield_active:
            self.shield_regen_timer += dt
            if self.shield_regen_timer > 5.0:
                self.shield_regen_timer = 0
                self.shield_active = True
                self.shield_hp = self.shield_max

    def draw(self, surface, camera):
        super().draw(surface, camera)
        if self.shield_active:
            sx, sy = camera.world_to_screen(self.x, self.y)
            ratio = self.shield_hp / self.shield_max
            pygame.draw.circle(surface, (100, 255, 100), (int(sx), int(sy)), self.radius + 6, 3)


class Healer(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=70, speed=60, damage=8, score_value=400, coin_value=6)
        self.color = (220, 220, 60)
        self.radius = 13
        self.name = "Healer"
        self.tier = 2
        self.heal_cooldown = 3.0
        self.heal_timer = 0
        self.heal_range = 150
        self.heal_amount = 15

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)
        self.heal_timer += dt

    def heal_nearby(self, enemies, particle_system):
        if self.heal_timer >= self.heal_cooldown:
            self.heal_timer = 0
            for e in enemies:
                if e is not self and e.alive:
                    dist = math.hypot(e.x - self.x, e.y - self.y)
                    if dist < self.heal_range:
                        e.hp = min(e.max_hp, e.hp + self.heal_amount)
                        for _ in range(5):
                            particle_system.spawn(e.x, e.y,
                                random.uniform(-30, 30), random.uniform(-60, -20),
                                (100, 255, 100), 0.5, 4)


class Bomber(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=50, speed=70, damage=40, score_value=300, coin_value=5)
        self.color = (255, 80, 0)
        self.radius = 14
        self.name = "Bomber"
        self.tier = 2
        self.explode_range = 80
        self.explode_threshold = 60

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < self.explode_range:
            self.explode(player, particle_system)

    def explode(self, player, particle_system):
        self.alive = False
        player.take_damage(self.damage)
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(80, 300)
            particle_system.spawn(self.x, self.y,
                math.cos(angle) * spd, math.sin(angle) * spd,
                (255, random.randint(80, 180), 0), random.uniform(0.4, 1.0), random.uniform(4, 10))


class Phantom(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=55, speed=90, damage=18, score_value=350, coin_value=5)
        self.color = (160, 100, 220)
        self.radius = 13
        self.name = "Phantom"
        self.tier = 3
        self.phase_timer = 0
        self.phase_duration = 2.0
        self.phased = False
        self.phase_cooldown = 3.0
        self.alpha = 255

    def take_damage(self, amount, kx=0, ky=0):
        if self.phased:
            return
        super().take_damage(amount, kx, ky)

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.phase_timer += dt
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if not self.phased and self.phase_timer > self.phase_cooldown and dist < 200:
            self.phased = True
            self.phase_timer = 0
        if self.phased:
            self.alpha = 80
            if self.phase_timer > self.phase_duration:
                self.phased = False
                self.phase_timer = 0
                self.alpha = 255
        self.move_toward_player(player.x, player.y, dt, walls)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = self.color if self.flash_timer <= 0 else (255, 255, 255)
        surf = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
        alpha = 80 if self.phased else 255
        pygame.draw.circle(surf, (*color, alpha), (self.radius + 1, self.radius + 1), self.radius)
        surface.blit(surf, (int(sx) - self.radius - 1, int(sy) - self.radius - 1))
        bar_w = self.radius * 2
        bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (80, 0, 0), (int(sx) - self.radius, int(sy) - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surface, (0, 220, 0), (int(sx) - self.radius, int(sy) - self.radius - 8, int(bar_w * ratio), bar_h))


class Necromancer(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=100, speed=45, damage=15, score_value=500, coin_value=8)
        self.color = (100, 0, 150)
        self.radius = 16
        self.name = "Necromancer"
        self.tier = 3
        self.summon_cooldown = 8.0
        self.summon_timer = 0
        self.max_summons = 2
        self.summons = []

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)
        self.summon_timer += dt
        self.summons = [s for s in self.summons if s.alive]

    def try_summon(self, particle_system):
        if self.summon_timer >= self.summon_cooldown and len(self.summons) < self.max_summons:
            self.summon_timer = 0
            angle = random.uniform(0, math.pi * 2)
            sx = self.x + math.cos(angle) * 60
            sy = self.y + math.sin(angle) * 60
            grunt = Grunt(sx, sy)
            grunt.hp = 20
            grunt.max_hp = 20
            self.summons.append(grunt)
            for _ in range(10):
                particle_system.spawn(sx, sy,
                    random.uniform(-40, 40), random.uniform(-40, 40),
                    (150, 0, 200), 0.5, 5)
            return grunt
        return None


class Titan(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=300, speed=35, damage=35, score_value=800, coin_value=12)
        self.color = (60, 60, 60)
        self.radius = 28
        self.name = "Titan"
        self.tier = 3
        self.stomp_cooldown = 4.0
        self.stomp_timer = 0
        self.stomp_range = 120
        self.armor = 5

    def take_damage(self, amount, kx=0, ky=0):
        reduced = max(1, amount - self.armor)
        super().take_damage(reduced, kx * 0.3, ky * 0.3)

    def update(self, dt, player, walls, particle_system):
        self.update_status_effects(dt)
        self.move_toward_player(player.x, player.y, dt, walls)
        self.stomp_timer += dt
        if self.stomp_timer >= self.stomp_cooldown:
            dist = math.hypot(player.x - self.x, player.y - self.y)
            if dist < self.stomp_range:
                self.stomp_timer = 0
                player.take_damage(self.damage)
                for _ in range(20):
                    angle = random.uniform(0, math.pi * 2)
                    particle_system.spawn(self.x, self.y,
                        math.cos(angle) * 150, math.sin(angle) * 150,
                        (100, 100, 100), 0.5, 6)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surface, color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, (40, 40, 40), (int(sx), int(sy)), self.radius, 3)
        bar_w = self.radius * 2
        bar_h = 5
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (80, 0, 0), (int(sx) - self.radius, int(sy) - self.radius - 10, bar_w, bar_h))
        pygame.draw.rect(surface, (0, 220, 0), (int(sx) - self.radius, int(sy) - self.radius - 10, int(bar_w * ratio), bar_h))


ENEMY_TYPES = {
    'grunt': Grunt,
    'speeder': Speeder,
    'brute': Brute,
    'shooter': Shooter,
    'shielder': Shielder,
    'healer': Healer,
    'bomber': Bomber,
    'phantom': Phantom,
    'necromancer': Necromancer,
    'titan': Titan,
}

# filename: bosses.py
import pygame
import math
import random
from constants import *
from particles import ParticleSystem

class BossBase:
    def __init__(self, x, y, name, hp, speed):
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.alive = True
        self.phase = 1
        self.radius = 40
        self.color = (200, 50, 50)
        self.vx = 0
        self.vy = 0
        self.flash_timer = 0
        self.stun_timer = 0
        self.invuln_timer = 0
        self.death_timer = 0
        self.dying = False
        self.projectiles = []
        self.attack_timer = 0
        self.move_timer = 0
        self.vulnerability_window = False
        self.vuln_timer = 0
        self.damage = 20
        self.score_value = 5000
        self.coin_value = 30
        self.death_particles_spawned = False
        self.phase2_threshold = 0.6
        self.phase3_threshold = 0.3
        self.phase_transition = False
        self.phase_transition_timer = 0
        self.tier = 4

    def take_damage(self, amount, kx=0, ky=0):
        if self.invuln_timer > 0:
            return
        if not self.vulnerability_window and not self.dying:
            amount *= 0.3
        self.hp -= amount
        self.flash_timer = 0.1
        if self.hp <= 0 and not self.dying:
            self.hp = 0
            self.dying = True
            self.death_timer = 2.0

    def update_phase(self, particle_system):
        ratio = self.hp / self.max_hp
        new_phase = self.phase
        if ratio <= self.phase3_threshold and self.phase < 3:
            new_phase = 3
        elif ratio <= self.phase2_threshold and self.phase < 2:
            new_phase = 2
        if new_phase != self.phase:
            self.phase = new_phase
            self.phase_transition = True
            self.phase_transition_timer = 1.5
            self.invuln_timer = 1.5
            for _ in range(40):
                angle = random.uniform(0, math.pi * 2)
                spd = random.uniform(100, 400)
                particle_system.spawn(self.x, self.y,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    self.color, random.uniform(0.5, 1.5), random.uniform(5, 12))

    def update_base(self, dt, player, particle_system):
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        if self.vuln_timer > 0:
            self.vuln_timer -= dt
            if self.vuln_timer <= 0:
                self.vulnerability_window = False
        if self.phase_transition_timer > 0:
            self.phase_transition_timer -= dt
            if self.phase_transition_timer <= 0:
                self.phase_transition = False
        for proj in self.projectiles:
            proj['x'] += proj['vx'] * dt
            proj['y'] += proj['vy'] * dt
            proj['lifetime'] -= dt
            dx = proj['x'] - player.x
            dy = proj['y'] - player.y
            if math.hypot(dx, dy) < player.radius + proj.get('radius', 8):
                if not player.dashing:
                    player.take_damage(proj['damage'])
                proj['lifetime'] = 0
        self.projectiles = [p for p in self.projectiles if p['lifetime'] > 0]
        if self.dying:
            self.death_timer -= dt
            if not self.death_particles_spawned:
                self.death_particles_spawned = True
                for _ in range(60):
                    angle = random.uniform(0, math.pi * 2)
                    spd = random.uniform(100, 500)
                    particle_system.spawn(self.x, self.y,
                        math.cos(angle) * spd, math.sin(angle) * spd,
                        self.color, random.uniform(1.0, 3.0), random.uniform(6, 16))
            if self.death_timer <= 0:
                self.alive = False

    def fire_at_player(self, player, speed=250, damage=None, radius=8, color=None):
        if damage is None:
            damage = self.damage
        if color is None:
            color = self.color
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.projectiles.append({
                'x': self.x, 'y': self.y,
                'vx': dx / dist * speed,
                'vy': dy / dist * speed,
                'damage': damage,
                'lifetime': 4.0,
                'radius': radius,
                'color': color
            })

    def fire_spread(self, player, count=8, speed=200, damage=None, color=None):
        if damage is None:
            damage = self.damage
        if color is None:
            color = self.color
        dx = player.x - self.x
        dy = player.y - self.y
        base_angle = math.atan2(dy, dx)
        spread = math.pi * 2 / count
        for i in range(count):
            angle = base_angle + spread * i
            self.projectiles.append({
                'x': self.x, 'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'damage': damage,
                'lifetime': 4.0,
                'radius': 8,
                'color': color
            })

    def draw_base(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        if self.vulnerability_window:
            glow_color = (255, 255, 0)
            pygame.draw.circle(surface, glow_color, (int(sx), int(sy)), self.radius + 8, 4)
        pygame.draw.circle(surface, color, (int(sx), int(sy)), self.radius)
        for proj in self.projectiles:
            px, py = camera.world_to_screen(proj['x'], proj['y'])
            pygame.draw.circle(surface, proj.get('color', (255, 100, 100)),
                (int(px), int(py)), proj.get('radius', 8))
        bar_w = 200
        bar_h = 12
        bx = int(sx) - bar_w // 2
        by = int(sy) - self.radius - 20
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (80, 0, 0), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, (220, 0, 0), (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 2)
        font = pygame.font.SysFont(None, 20)
        txt = font.render(f"{self.name} P{self.phase}", True, (255, 255, 255))
        surface.blit(txt, (bx, by - 18))


class BossIronclad(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Ironclad", hp=800, speed=70)
        self.color = (100, 120, 160)
        self.radius = 38
        self.armor_plates = 4
        self.stomp_cooldown = 3.0
        self.stomp_timer = 0
        self.spin_active = False
        self.spin_timer = 0
        self.spin_angle = 0
        self.laser_active = False
        self.laser_timer = 0
        self.laser_angle = 0
        self.laser_cooldown = 8.0
        self.laser_cd_timer = 0
        self.shield_timer = 0
        self.shield_active = False
        self.shield_cooldown = 12.0
        self.shield_cd_timer = 0
        self.shield_hp = 0
        self.move_target_x = x
        self.move_target_y = y

    def update(self, dt, player, walls, particle_system):
        self.update_base(dt, player, particle_system)
        if self.dying or self.phase_transition:
            return
        self.update_phase(particle_system)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        spd = self.speed * (1.0 + (self.phase - 1) * 0.3)
        if dist > 60:
            self.x += dx / dist * spd * dt
            self.y += dy / dist * spd * dt
        self.attack_timer += dt
        self.stomp_timer += dt
        self.laser_cd_timer += dt
        self.shield_cd_timer += dt
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
        else:
            if self.shield_cd_timer >= self.shield_cooldown and self.phase >= 2:
                self.shield_cd_timer = 0
                self.shield_active = True
                self.shield_timer = 4.0
                self.shield_hp = 100
                self.vulnerability_window = False
                for _ in range(15):
                    angle = random.uniform(0, math.pi * 2)
                    particle_system.spawn(self.x, self.y,
                        math.cos(angle) * 80, math.sin(angle) * 80,
                        (150, 180, 255), 0.5, 6)
        if self.laser_active:
            self.laser_timer -= dt
            self.laser_angle += dt * (2.0 + self.phase * 0.5)
            dx2 = player.x - self.x
            dy2 = player.y - self.y
            target_angle = math.atan2(dy2, dx2)
            self.laser_angle = self.laser_angle * 0.9 + target_angle * 0.1
            end_x = self.x + math.cos(self.laser_angle) * 600
            end_y = self.y + math.sin(self.laser_angle) * 600
            dist_to_laser = abs((end_y - self.y) * player.x - (end_x - self.x) * player.y +
                end_x * self.y - end_y * self.x) / math.hypot(end_x - self.x, end_y - self.y + 0.001)
            fwd = ((player.x - self.x) * math.cos(self.laser_angle) +
                   (player.y - self.y) * math.sin(self.laser_angle))
            if dist_to_laser < 20 and fwd > 0:
                player.take_damage(40 * dt)
                particle_system.spawn(player.x, player.y,
                    random.uniform(-50, 50), random.uniform(-80, -20),
                    (255, 200, 50), 0.2, 4)
            if self.laser_timer <= 0:
                self.laser_active = False
                self.vulnerability_window = True
                self.vuln_timer = 2.0
        else:
            if self.laser_cd_timer >= self.laser_cooldown and self.phase >= 1:
                self.laser_cd_timer = 0
                self.laser_active = True
                self.laser_timer = 3.0
                self.laser_angle = math.atan2(player.y - self.y, player.x - self.x)
        if self.stomp_timer >= self.stomp_cooldown and dist < 100:
            self.stomp_timer = 0
            player.take_damage(self.damage)
            for _ in range(20):
                angle = random.uniform(0, math.pi * 2)
                particle_system.spawn(self.x, self.y,
                    math.cos(angle) * 200, math.sin(angle) * 200,
                    (150, 180, 220), 0.4, 7)
        attack_rate = 2.0 - (self.phase - 1) * 0.4
        if self.attack_timer >= attack_rate:
            self.attack_timer = 0
            if self.phase == 1:
                self.fire_at_player(player)
            elif self.phase == 2:
                self.fire_spread(player, count=5, speed=220)
            else:
                self.fire_spread(player, count=8, speed=260, damage=self.damage * 1.3)
                self.fire_at_player(player, speed=300, damage=self.damage * 1.5)

    def take_damage(self, amount, kx=0, ky=0):
        if self.shield_active:
            self.shield_hp -= amount
            self.flash_timer = 0.1
            if self.shield_hp <= 0:
                self.shield_active = False
                self.vulnerability_window = True
                self.vuln_timer = 2.5
        else:
            super().take_damage(amount, kx, ky)

    def draw(self, surface, camera):
        self.draw_base(surface, camera)
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.laser_active:
            end_x = self.x + math.cos(self.laser_angle) * 600
            end_y = self.y + math.sin(self.laser_angle) * 600
            ex, ey = camera.world_to_screen(end_x, end_y)
            pygame.draw.line(surface, (255, 220, 50), (int(sx), int(sy)), (int(ex), int(ey)), 4)
            pygame.draw.line(surface, (255, 255, 200), (int(sx), int(sy)), (int(ex), int(ey)), 2)
        if self.shield_active:
            ratio = max(0, self.shield_hp / 100)
            color = (int(100 * ratio), int(150 * ratio), 255)
            pygame.draw.circle(surface, color, (int(sx), int(sy)), self.radius + 12, 4)


class BossVoidweaver(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Voidweaver", hp=1000, speed=90)
        self.color = (80, 0, 160)
        self.radius = 36
        self.teleport_cooldown = 5.0
        self.teleport_timer = 0
        self.clone_list = []
        self.clone_cooldown = 12.0
        self.clone_timer = 0
        self.vortex_active = False
        self.vortex_timer = 0
        self.vortex_cooldown = 10.0
        self.vortex_cd_timer = 0
        self.pattern_index = 0
        self.orbit_angle = 0
        self.orbit_radius = 200
        self.score_value = 8000
        self.coin_value = 50

    def update(self, dt, player, walls, particle_system):
        self.update_base(dt, player, particle_system)
        if self.dying or self.phase_transition:
            return
        self.update_phase(particle_system)
        self.orbit_angle += dt * (0.8 + self.phase * 0.3)
        target_x = player.x + math.cos(self.orbit_angle) * self.orbit_radius
        target_y = player.y + math.sin(self.orbit_angle) * self.orbit_radius
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        spd = self.speed
        if dist > 10:
            self.x += dx / dist * min(spd * dt, dist)
            self.y += dy / dist * min(spd * dt, dist)
        self.teleport_timer += dt
        self.clone_timer += dt
        self.vortex_cd_timer += dt
        self.attack_timer += dt
        if self.teleport_timer >= self.teleport_cooldown and self.phase >= 2:
            self.teleport_timer = 0
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                particle_system.spawn(self.x, self.y,
                    math.cos(angle) * 100, math.sin(angle) * 100,
                    (120, 0, 220), 0.5, 6)
            angle = random.uniform(0, math.pi * 2)
            self.x = player.x + math.cos(angle) * random.uniform(150, 300)
            self.y = player.y + math.sin(angle) * random.uniform(150, 300)
            self.vulnerability_window = True
            self.vuln_timer = 1.0
            for _ in range(8):
                angle2 = random.uniform(0, math.pi * 2)
                particle_system.spawn(self.x, self.y,
                    math.cos(angle2) * 100, math.sin(angle2) * 100,
                    (200, 100, 255), 0.5, 6)
        if self.vortex_cd_timer >= self.vortex_cooldown and self.phase >= 1:
            self.vortex_cd_timer = 0
            self.vortex_active = True
            self.vortex_timer = 3.0 + self.phase
        if self.vortex_active:
            self.vortex_timer -= dt
            dx2 = self.x - player.x
            dy2 = self.y - player.y
            dist2 = math.hypot(dx2, dy2) + 0.001
            pull = 120 + self.phase * 40
            player.vx += (dx2 / dist2) * (-pull) * dt
            player.vy += (dy2 / dist2) * (-pull) * dt
            if self.vortex_timer <= 0:
                self.vortex_active = False
                self.vulnerability_window = True
                self.vuln_timer = 2.0
        if self.clone_timer >= self.clone_cooldown and self.phase == 3:
            self.clone_timer = 0
            self.clone_list = []
            for i in range(2):
                angle = random.uniform(0, math.pi * 2)
                cx = self.x + math.cos(angle) * 150
                cy = self.y + math.sin(angle) * 150
                self.clone_list.append({'x': cx, 'y': cy, 'hp': 50, 'alive': True})
        attack_rate = 1.8 - (self.phase - 1) * 0.3
        if self.attack_timer >= attack_rate:
            self.attack_timer = 0
            n = 6 + self.phase * 2
            self.fire_spread(player, count=n, speed=180 + self.phase * 30,
                color=(140, 60, 255), damage=self.damage)

    def draw(self, surface, camera):
        self.draw_base(surface, camera)
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.vortex_active:
            for r in range(3):
                rad = int(80 + r * 40 + math.sin(pygame.time.get_ticks() * 0.005 + r) * 20)
                alpha_surf = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surf, (100, 0, 200, 40), (rad, rad), rad, 3)
                surface.blit(alpha_surf, (int(sx) - rad, int(sy) - rad))
        for clone in self.clone_list:
            if clone['alive']:
                cx, cy = camera.world_to_screen(clone['x'], clone['y'])
                pygame.draw.circle(surface, (120, 60, 200), (int(cx), int(cy)), 20)


class BossInferno(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Inferno", hp=1200, speed=60)
        self.color = (220, 80, 0)
        self.radius = 42
        self.fireball_cooldown = 1.5
        self.fireball_timer = 0
        self.meteor_cooldown = 8.0
        self.meteor_timer = 0
        self.meteors = []
        self.flame_wall_cooldown = 12.0
        self.flame_wall_timer = 0
        self.flame_walls = []
        self.enrage = False
        self.enrage_timer = 0
        self.lava_pools = []
        self.score_value = 10000
        self.coin_value = 80
        self.damage = 25

    def update(self, dt, player, walls, particle_system):
        self.update_base(dt, player, particle_system)
        if self.dying or self.phase_transition:
            return
        self.update_phase(particle_system)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy) + 0.001
        spd = self.speed * (1.0 + (self.phase - 1) * 0.2)
        if dist > 80:
            self.x += dx / dist * spd * dt
            self.y += dy / dist * spd * dt
        if self.phase == 3 and not self.enrage:
            self.enrage = True
            self.fireball_cooldown = 0.