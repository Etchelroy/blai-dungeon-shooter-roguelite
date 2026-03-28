import pygame
import math
import random
from settings import *
from weapons import create_weapon
from abilities import create_ability

class Player:
    def __init__(self, pos, particles, effects):
        self.pos = list(pos)
        self.vel = [0.0, 0.0]
        self.particles = particles
        self.effects = effects
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.speed = PLAYER_SPEED
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_timer = 0.0
        self.dash_active = False
        self.dash_vel = [0.0, 0.0]
        self.dash_duration = 0.15
        self.dash_duration_timer = 0.0
        self.invincible = False
        self.invincible_timer = 0.0
        self.radius = 12
        self.facing = 0.0
        self.afterimages = []
        self.coins = 0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.kills = 0
        self.weapon_index = 0
        self.weapons = [create_weapon('pistol'), create_weapon('shotgun')]
        self.current_weapon = self.weapons[self.weapon_index]
        self.ability = create_ability('shield')
        self.upgrades = {}
        self.melee_cooldown = 0.0
        self.melee_range = 60
        self.melee_damage = 30
        self.dead = False
        self.shoot_timer = 0.0
        self.anim_timer = 0.0
        self.walk_frame = 0
        self.color = (50, 200, 255)

    def handle_input(self, keys, dt, bullets, camera):
        move_x, move_y = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        if not self.dash_active:
            length = math.sqrt(move_x**2 + move_y**2)
            if length > 0:
                move_x /= length
                move_y /= length
            target_vx = move_x * self.speed
            target_vy = move_y * self.speed
            friction = 0.85
            self.vel[0] = self.vel[0] * friction + target_vx * (1 - friction) * 10 * dt * 60
            self.vel[1] = self.vel[1] * friction + target_vy * (1 - friction) * 10 * dt * 60
        else:
            self.vel[0] = self.dash_vel[0]
            self.vel[1] = self.dash_vel[1]

        mx, my = pygame.mouse.get_pos()
        wx = mx + camera.x
        wy = my + camera.y
        dx = wx - self.pos[0]
        dy = wy - self.pos[1]
        self.facing = math.atan2(dy, dx)

    def attempt_dash(self, keys):
        if keys[pygame.K_SPACE] and self.dash_timer <= 0 and not self.dash_active:
            vx, vy = self.vel[0], self.vel[1]
            length = math.sqrt(vx**2 + vy**2)
            if length < 50:
                vx = math.cos(self.facing)
                vy = math.sin(self.facing)
                length = 1
            self.dash_vel = [vx / length * DASH_SPEED, vy / length * DASH_SPEED]
            self.dash_active = True
            self.dash_duration_timer = self.dash_duration
            self.dash_timer = self.dash_cooldown
            self.invincible = True
            self.invincible_timer = self.dash_duration + 0.1
            self.afterimages = []
            return True
        return False

    def attempt_melee(self, keys, enemies):
        if keys[pygame.K_e] and self.melee_cooldown <= 0:
            self.melee_cooldown = 0.5
            hit_enemies = []
            for e in enemies:
                dx = e.pos[0] - self.pos[0]
                dy = e.pos[1] - self.pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                angle_to = math.atan2(dy, dx)
                angle_diff = abs(((angle_to - self.facing) + math.pi) % (2*math.pi) - math.pi)
                if dist < self.melee_range and angle_diff < math.pi * 0.6:
                    hit_enemies.append(e)
                    e.take_damage(self.melee_damage)
                    self.particles.emit('spark', e.pos[0], e.pos[1], count=8, color=(255,200,50))
            self.effects.screen_shake(3, 0.1)
            return hit_enemies
        return []

    def update(self, dt, tilemap, bullets, camera, keys, enemies):
        self.anim_timer += dt
        if self.anim_timer > 0.15:
            self.anim_timer = 0
            self.walk_frame = (self.walk_frame + 1) % 4

        self.handle_input(keys, dt, bullets, camera)
        self.attempt_dash(keys)
        self.attempt_melee(keys, enemies)

        if self.dash_active:
            self.dash_duration_timer -= dt
            self.afterimages.append({
                'pos': self.pos[:],
                'alpha': 200,
                'facing': self.facing
            })
            if self.dash_duration_timer <= 0:
                self.dash_active = False
                self.vel[0] *= 0.3
                self.vel[1] *= 0.3

        for img in self.afterimages:
            img['alpha'] -= dt * 800
        self.afterimages = [a for a in self.afterimages if a['alpha'] > 0]

        new_x = self.pos[0] + self.vel[0] * dt
        new_y = self.pos[1] + self.vel[1] * dt

        if tilemap and not tilemap.is_wall(new_x, self.pos[1], self.radius):
            self.pos[0] = new_x
        else:
            self.vel[0] *= -0.3
        if tilemap and not tilemap.is_wall(self.pos[0], new_y, self.radius):
            self.pos[1] = new_y
        else:
            self.vel[1] *= -0.3

        self.pos[0] = max(self.radius, min(ARENA_W - self.radius, self.pos[0]))
        self.pos[1] = max(self.radius, min(ARENA_H - self.radius, self.pos[1]))

        if self.dash_timer > 0:
            self.dash_timer -= dt
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
        if self.melee_cooldown > 0:
            self.melee_cooldown -= dt
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.ability:
            self.ability.update(dt)

        moving = abs(self.vel[0]) > 20 or abs(self.vel[1]) > 20
        if moving:
            if random.random() < 0.1:
                self.particles.emit('dust', self.pos[0], self.pos[1], count=1)

    def shoot(self, bullets):
        weapon = self.current_weapon
        if not weapon:
            return
        if self.shoot_timer > 0:
            return
        new_bullets = weapon.fire(self.pos[:], self.facing, self.upgrades)
        bullets.extend(new_bullets)
        self.shoot_timer = weapon.fire_rate
        if new_bullets:
            self.effects.screen_shake(weapon.shake, 0.05)
            self.particles.emit('muzzle', self.pos[0] + math.cos(self.facing)*20,
                               self.pos[1] + math.sin(self.facing)*20, count=3,
                               color=weapon.color)

    def take_damage(self, amount):
        if self.invincible or self.dead:
            return False
        if self.ability and hasattr(self.ability, 'block_damage') and self.ability.active:
            self.effects.screen_flash((100, 150, 255), 0.1)
            return False
        self.hp -= amount
        self.invincible = True
        self.invincible_timer = 0.5
        self.effects.screen_shake(8, 0.2)
        self.effects.screen_flash((255, 50, 50), 0.15)
        self.particles.emit('blood', self.pos[0], self.pos[1], count=15)
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return True

    def add_kill(self, value=1):
        self.kills += 1
        self.combo += 1
        self.combo_timer = 3.0
        multiplier = min(self.combo, 10)
        self.score += value * multiplier * 10
        self.coins += max(1, value)

    def switch_weapon(self, direction):
        if not self.weapons:
            return
        self.weapon_index = (self.weapon_index + direction) % len(self.weapons)
        self.current_weapon = self.weapons[self.weapon_index]

    def add_weapon(self, weapon):
        self.weapons.append(weapon)

    def draw(self, surface, camera):
        sx = self.pos[0] - camera.x
        sy = self.pos[1] - camera.y

        for img in self.afterimages:
            asx = img['pos'][0] - camera.x
            asy = img['pos'][1] - camera.y
            alpha = int(img['alpha'])
            after_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(after_surf, (*self.color[:3], alpha), (15, 15), 12)
            surface.blit(after_surf, (asx - 15, asy - 15))

        body_color = self.color
        if self.invincible and not self.dash_active:
            t = pygame.time.get_ticks() / 1000
            if int(t * 10) % 2 == 0:
                body_color = (255, 255, 255)

        pygame.draw.circle(surface, (30, 30, 50), (int(sx), int(sy) + 4), 13)
        pygame.draw.circle(surface, body_color, (int(sx), int(sy)), 12)
        pygame.draw.circle(surface, (200, 230, 255), (int(sx), int(sy)), 12, 2)

        eye_x = sx + math.cos(self.facing) * 6
        eye_y = sy + math.sin(self.facing) * 6
        pygame.draw.circle(surface, (255, 255, 100), (int(eye_x), int(eye_y)), 4)
        pygame.draw.circle(surface, (50, 50, 0), (int(eye_x), int(eye_y)), 2)

        gun_x = sx + math.cos(self.facing) * 18
        gun_y = sy + math.sin(self.facing) * 18
        gun_color = self.current_weapon.color if self.current_weapon else (150, 150, 150)
        pygame.draw.line(surface, gun_color, (int(sx), int(sy)), (int(gun_x), int(gun_y)), 4)

        if self.ability and self.ability.active and hasattr(self.ability, 'block_damage'):
            shield_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            alpha = 120 + int(math.sin(pygame.time.get_ticks() / 200) * 40)
            pygame.draw.circle(shield_surf, (100, 150, 255, alpha), (25, 25), 24, 3)
            surface.blit(shield_surf, (int(sx) - 25, int(sy) - 25))

        if hasattr(self.ability, 'sentries'):
            for s in self.ability.sentries:
                ssx = s['pos'][0] - camera.x
                ssy = s['pos'][1] - camera.y
                pygame.draw.circle(surface, (50, 255, 150), (int(ssx), int(ssy)), 8)
                pygame.draw.circle(surface, (200, 255, 220), (int(ssx), int(ssy)), 8, 2)