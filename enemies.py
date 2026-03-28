import pygame
import math
import random
from constants import *

class EnemyBase:
    tier = 1
    def __init__(self, x, y, hp, speed, color, size=24):
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.color = color
        self.size = size
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.stun_timer = 0.0
        self.damage_flash = 0.0
        self.drop_coins = 1
        self.score_value = 100
        self.attack_timer = 0.0
        self.attack_cooldown = 1.5
        self.damage = 10
        self.image = self._make_image()
        self.angle = 0.0
        self.knockback_x = 0.0
        self.knockback_y = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surf, (255,255,255), (self.size, self.size), self.size, 2)
        return surf

    def get_rect(self):
        return pygame.Rect(int(self.x - self.size), int(self.y - self.size), self.size*2, self.size*2)

    def take_damage(self, amount, kx=0, ky=0):
        self.hp -= amount
        self.damage_flash = 0.3
        self.knockback_x = kx * 200
        self.knockback_y = ky * 200
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def stun(self, duration):
        self.stun_timer = duration

    def update(self, dt, player, walls, projectiles_out):
        if self.stun_timer > 0:
            self.stun_timer -= dt
        if self.damage_flash > 0:
            self.damage_flash -= dt
        self.knockback_x *= (1 - 8*dt)
        self.knockback_y *= (1 - 8*dt)
        if self.attack_timer > 0:
            self.attack_timer -= dt

        if self.stun_timer <= 0:
            self.ai_update(dt, player, walls, projectiles_out)

        self.x += self.knockback_x * dt
        self.y += self.knockback_y * dt
        self._clamp_walls(walls)

    def ai_update(self, dt, player, walls, projectiles_out):
        pass

    def _move_toward(self, tx, ty, dt, walls):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            nx, ny = dx/dist, dy/dist
            old_x, old_y = self.x, self.y
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt
            if self._check_walls(walls):
                self.x, self.y = old_x, old_y
                # try sliding
                self.x = old_x + nx * self.speed * dt
                if self._check_walls(walls):
                    self.x = old_x
                    self.y = old_y + ny * self.speed * dt
                    if self._check_walls(walls):
                        self.y = old_y

    def _check_walls(self, walls):
        r = self.get_rect()
        for w in walls:
            if r.colliderect(w):
                return True
        return False

    def _clamp_walls(self, walls):
        if self._check_walls(walls):
            pass

    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x)
        sy = int(self.y - camera.offset_y)
        if self.damage_flash > 0 and int(self.damage_flash*20)%2==0:
            img = self.image.copy()
            img.fill((255,100,100,0), special_flags=pygame.BLEND_ADD)
            surface.blit(img, (sx - self.size, sy - self.size))
        else:
            surface.blit(self.image, (sx - self.size, sy - self.size))
        # HP bar
        if self.hp < self.max_hp:
            bar_w = self.size*2
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, (80,0,0), (sx - self.size, sy - self.size - 8, bar_w, 5))
            pygame.draw.rect(surface, (220,50,50), (sx - self.size, sy - self.size - 8, int(bar_w*ratio), 5))

# ---- Tier 1 ----
class Grunt(EnemyBase):
    tier = 1
    def __init__(self, x, y):
        super().__init__(x, y, hp=40, speed=80, color=(200, 80, 80), size=14)
        self.drop_coins = 1
        self.score_value = 100
        self.damage = 8
        self.attack_cooldown = 1.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.polygon(surf, self.color, [
            (self.size, 2), (self.size*2-2, self.size*2-2), (2, self.size*2-2)])
        pygame.draw.polygon(surf, (255,150,150), [
            (self.size, 2), (self.size*2-2, self.size*2-2), (2, self.size*2-2)], 2)
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        self._move_toward(player.x, player.y, dt, walls)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 30 and self.attack_timer <= 0:
            player.take_damage(self.damage)
            self.attack_timer = self.attack_cooldown

class Shooter(EnemyBase):
    tier = 1
    def __init__(self, x, y):
        super().__init__(x, y, hp=30, speed=50, color=(80, 80, 220), size=14)
        self.drop_coins = 1
        self.score_value = 120
        self.damage = 12
        self.attack_cooldown = 2.0
        self.preferred_range = 200

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surf, (150, 150, 255), (self.size, self.size), self.size//2)
        pygame.draw.circle(surf, (255,255,255), (self.size, self.size), self.size, 2)
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist > self.preferred_range + 50:
            self._move_toward(player.x, player.y, dt, walls)
        elif dist < self.preferred_range - 50:
            dx = self.x - player.x
            dy = self.y - player.y
            d = math.hypot(dx, dy)
            if d > 0:
                self.x += dx/d * self.speed * dt
                self.y += dy/d * self.speed * dt

        if self.attack_timer <= 0 and dist < 300:
            self.attack_timer = self.attack_cooldown
            from projectiles import EnemyProjectile
            dx = player.x - self.x
            dy = player.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                proj = EnemyProjectile(self.x, self.y, dx/d, dy/d, speed=200, damage=self.damage, color=(100,100,255))
                projectiles_out.append(proj)

class Charger(EnemyBase):
    tier = 1
    def __init__(self, x, y):
        super().__init__(x, y, hp=60, speed=60, color=(220, 140, 40), size=18)
        self.drop_coins = 2
        self.score_value = 150
        self.damage = 20
        self.attack_cooldown = 3.0
        self.charging = False
        self.charge_vx = 0
        self.charge_vy = 0
        self.charge_timer = 0.0
        self.windup_timer = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, self.color, (0, 4, self.size*2, self.size*2-8))
        pygame.draw.polygon(surf, (255,200,80), [(self.size, 0),(self.size+8, 10),(self.size-8,10)])
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        if self.charging:
            self.charge_timer -= dt
            old_x, old_y = self.x, self.y
            self.x += self.charge_vx * dt
            self.y += self.charge_vy * dt
            if self._check_walls(walls):
                self.x, self.y = old_x, old_y
                self.charging = False
            dist = math.hypot(player.x - self.x, player.y - self.y)
            if dist < 25:
                player.take_damage(self.damage)
                self.charging = False
            if self.charge_timer <= 0:
                self.charging = False
        elif self.windup_timer > 0:
            self.windup_timer -= dt
            if self.windup_timer <= 0:
                self.charging = True
                self.charge_timer = 0.5
                dx = player.x - self.x
                dy = player.y - self.y
                d = math.hypot(dx, dy)
                if d > 0:
                    self.charge_vx = dx/d * 400
                    self.charge_vy = dy/d * 400
        else:
            self._move_toward(player.x, player.y, dt, walls)
            dist = math.hypot(player.x - self.x, player.y - self.y)
            if dist < 150 and self.attack_timer <= 0:
                self.attack_timer = self.attack_cooldown
                self.windup_timer = 0.5

# ---- Tier 2 ----
class Shielder(EnemyBase):
    tier = 2
    def __init__(self, x, y):
        super().__init__(x, y, hp=120, speed=55, color=(100, 200, 100), size=20)
        self.drop_coins = 3
        self.score_value = 250
        self.damage = 15
        self.shielded = True
        self.shield_hp = 60
        self.attack_cooldown = 1.5

    def take_damage(self, amount, kx=0, ky=0):
        if self.shielded:
            self.shield_hp -= amount
            self.damage_flash = 0.2
            if self.shield_hp <= 0:
                self.shielded = False
        else:
            super().take_damage(amount, kx, ky)

    def ai_update(self, dt, player, walls, projectiles_out):
        self._move_toward(player.x, player.y, dt, walls)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 35 and self.attack_timer <= 0:
            player.take_damage(self.damage)
            self.attack_timer = self.attack_cooldown

    def draw(self, surface, camera):
        super().draw(surface, camera)
        if self.shielded:
            sx = int(self.x - camera.offset_x)
            sy = int(self.y - camera.offset_y)
            pygame.draw.circle(surface, (100,255,100,100), (sx,sy), self.size+4, 3)

class Bomber(EnemyBase):
    tier = 2
    def __init__(self, x, y):
        super().__init__(x, y, hp=50, speed=70, color=(220, 80, 220), size=16)
        self.drop_coins = 3
        self.score_value = 200
        self.damage = 40
        self.attack_cooldown = 4.0
        self.fuse_timer = -1

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surf, (255,100,255), (self.size, self.size), self.size//2)
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if self.fuse_timer > 0:
            self.fuse_timer -= dt
            if self.fuse_timer <= 0:
                if dist < MELEE_RANGE * 2:
                    player.take_damage(self.damage)
                self.alive = False
                from particles import spawn_explosion
                spawn_explosion(self.x, self.y, (255,150,50))
        else:
            self._move_toward(player.x, player.y, dt, walls)
            if dist < 50 and self.attack_timer <= 0:
                self.fuse_timer = 1.0
                self.attack_timer = self.attack_cooldown

class Sniper(EnemyBase):
    tier = 2
    def __init__(self, x, y):
        super().__init__(x, y, hp=45, speed=40, color=(80, 200, 200), size=14)
        self.drop_coins = 3
        self.score_value = 220
        self.damage = 30
        self.attack_cooldown = 3.5
        self.aim_timer = 0.0
        self.aiming = False
        self.aim_target = (0, 0)

    def ai_update(self, dt, player, walls, projectiles_out):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if not self.aiming:
            if dist > 250:
                self._move_toward(player.x, player.y, dt, walls)
            if self.attack_timer <= 0:
                self.aiming = True
                self.aim_timer = 1.5
                self.aim_target = (player.x, player.y)
        else:
            self.aim_timer -= dt
            if self.aim_timer <= 0:
                self.aiming = False
                self.attack_timer = self.attack_cooldown
                from projectiles import EnemyProjectile
                dx = self.aim_target[0] - self.x
                dy = self.aim_target[1] - self.y
                d = math.hypot(dx, dy)
                if d > 0:
                    proj = EnemyProjectile(self.x, self.y, dx/d, dy/d, speed=400, damage=self.damage,
                                          color=(50,255,255), piercing=True)
                    projectiles_out.append(proj)

    def draw(self, surface, camera):
        super().draw(surface, camera)
        if self.aiming:
            sx = int(self.x - camera.offset_x)
            sy = int(self.y - camera.offset_y)
            tx = int(self.aim_target[0] - camera.offset_x)
            ty = int(self.aim_target[1] - camera.offset_y)
            progress = 1.0 - (self.aim_timer / 1.5)
            color = (255, int(255*(1-progress)), 0)
            pygame.draw.line(surface, color, (sx,sy), (tx,ty), 1)

# ---- Tier 3 ----
class Berserker(EnemyBase):
    tier = 3
    def __init__(self, x, y):
        super().__init__(x, y, hp=200, speed=90, color=(220, 40, 40), size=22)
        self.drop_coins = 5
        self.score_value = 400
        self.damage = 25
        self.attack_cooldown = 0.8
        self.enraged = False

    def take_damage(self, amount, kx=0, ky=0):
        super().take_damage(amount, kx, ky)
        if self.hp < self.max_hp * 0.4 and not self.enraged:
            self.enraged = True
            self.speed = 150
            self.damage = 40

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.polygon(surf, self.color, [
            (self.size, 0), (self.size*2, self.size), (self.size*2-4, self.size*2),
            (4, self.size*2), (0, self.size)])
        if self.enraged:
            pygame.draw.polygon(surf, (255,100,0), [
                (self.size, 0), (self.size*2, self.size), (self.size*2-4, self.size*2),
                (4, self.size*2), (0, self.size)], 3)
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        self.image = self._make_image()
        self._move_toward(player.x, player.y, dt, walls)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 35 and self.attack_timer <= 0:
            player.take_damage(self.damage)
            self.attack_timer = self.attack_cooldown

class Summoner(EnemyBase):
    tier = 3
    def __init__(self, x, y):
        super().__init__(x, y, hp=150, speed=30, color=(180, 100, 220), size=22)
        self.drop_coins = 6
        self.score_value = 500
        self.damage = 8
        self.attack_cooldown = 5.0
        self.summon_count = 0
        self.max_summons = 4

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        for i in range(8):
            a = i * math.pi/4
            pygame.draw.line(surf, self.color,
                (self.size + math.cos(a)*8, self.size + math.sin(a)*8),
                (self.size + math.cos(a)*self.size, self.size + math.sin(a)*self.size), 2)
        pygame.draw.circle(surf, self.color, (self.size, self.size), 10)
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        self._move_toward(player.x, player.y, dt, walls)
        if self.attack_timer <= 0 and self.summon_count < self.max_summons:
            self.attack_timer = self.attack_cooldown
            return True  # signal to spawn grunt
        return False

    def update(self, dt, player, walls, projectiles_out):
        super().update(dt, player, walls, projectiles_out)
        if self.stun_timer <= 0:
            result = self.ai_update(dt, player, walls, projectiles_out)
            if result:
                offset = random.choice([(60,0),(-60,0),(0,60),(0,-60)])
                g = Grunt(self.x + offset[0], self.y + offset[1])
                projectiles_out.append(('spawn_enemy', g))
                self.summon_count += 1

class Necromancer(EnemyBase):
    tier = 3
    def __init__(self, x, y):
        super().__init__(x, y, hp=180, speed=35, color=(60, 80, 160), size=24)
        self.drop_coins = 7
        self.score_value = 600
        self.damage = 18
        self.attack_cooldown = 2.0
        self.phase = 0
        self.teleport_timer = 8.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, self.color, (0, self.size//2, self.size*2, self.size + self.size//2))
        pygame.draw.ellipse(surf, (100,120,220), (4, self.size//2+4, self.size*2-8, self.size-4))
        return surf

    def ai_update(self, dt, player, walls, projectiles_out):
        self.teleport_timer -= dt
        if self.teleport_timer <= 0:
            self.teleport_timer = 8.0
            self.x += random.uniform(-200, 200)
            self.y += random.uniform(-200, 200)

        if self.attack_timer <= 0:
            self.attack_timer = self.attack_cooldown
            from projectiles import EnemyProjectile
            for i in range(3):
                dx = player.x - self.x
                dy = player.y - self.y
                a = math.atan2(dy, dx) + (i-1) * 0.3
                proj = EnemyProjectile(self.x, self.y, math.cos(a), math.sin(a),
                                      speed=180, damage=self.damage, color=(80,80,220))
                projectiles_out.append(proj)

ENEMY_TYPES = [Grunt, Shooter, Charger, Shielder, Bomber, Sniper, Berserker, Summoner, Necromancer]
TIER1_ENEMIES = [Grunt, Shooter, Charger]
TIER2_ENEMIES = [Shielder, Bomber, Sniper]
TIER3_ENEMIES = [Berserker, Summoner, Necromancer]