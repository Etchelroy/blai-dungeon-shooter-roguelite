import pygame
import math
import random
from projectiles import Projectile, BombProjectile, ReturnProjectile, LaserBeam

class Weapon:
    def __init__(self, name, ammo, max_ammo, fire_rate, damage):
        self.name = name
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.fire_rate = fire_rate
        self.fire_timer = 0
        self.damage = damage
        self.color = (255, 220, 0)

    def update(self):
        if self.fire_timer > 0:
            self.fire_timer -= 1

    def can_fire(self):
        return self.fire_timer <= 0 and self.ammo > 0

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        pass

    def get_info(self):
        return f"{self.name} {self.ammo}/{self.max_ammo}"

class Pistol(Weapon):
    def __init__(self):
        super().__init__("PISTOL", 999, 999, 12, 20)
        self.color = (255, 220, 80)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        speed = 12
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        projectiles.append(Projectile(x, y, vx, vy, self.damage, (255, 220, 80), 5, life=90))

class Shotgun(Weapon):
    def __init__(self):
        super().__init__("SHOTGUN", 40, 40, 30, 15)
        self.color = (255, 150, 50)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        for i in range(7):
            spread = math.radians(random.uniform(-20, 20))
            a = angle + spread
            speed = random.uniform(9, 13)
            vx = math.cos(a) * speed
            vy = math.sin(a) * speed
            p = Projectile(x, y, vx, vy, self.damage, (255, 150, 50), 4, life=50)
            projectiles.append(p)

class RifleWeapon(Weapon):
    def __init__(self):
        super().__init__("RIFLE", 90, 90, 6, 25)
        self.color = (100, 220, 255)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        speed = 18
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        p = Projectile(x, y, vx, vy, self.damage, (100, 220, 255), 4,
                       pierce=True, max_pierce=3, life=120)
        projectiles.append(p)

class RocketLauncher(Weapon):
    def __init__(self):
        super().__init__("ROCKETS", 12, 12, 50, 80)
        self.color = (255, 80, 30)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        speed = 9
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        p = BombProjectile(x, y, vx, vy, self.damage, aoe_radius=90)
        projectiles.append(p)

class ChainGun(Weapon):
    def __init__(self):
        super().__init__("CHAIN", 120, 120, 5, 18)
        self.color = (180, 255, 100)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can_fire():
            return
        self.fire_timer = self.fire_rate
        self.ammo -= 1
        spread = math.radians(random.uniform(-5, 5))
        a = angle + spread
        speed = 14
        vx = math.cos(a) * speed
        vy = math.sin(a) * speed
        p = Projectile(x, y, vx, vy, self.damage, (180, 255, 100), 4,
                       chain=3, life=100)
        projectiles.append(p)

class Boomerang(Weapon):
    def __init__(self):
        super().__init__("BOOMERANG", 5, 5, 60, 35)
        self.active_boomerangs = 0
        self.color = (0, 220, 255)

    def fire(self, x, y, angle, projectiles, owner_ref=None):
        if not self.can
Looking at what's needed, I'll implement the remaining core systems. Let me build out all the missing modules.

```python
# filename: player.py
import pygame
import math
import time

class Afterimage:
    def __init__(self, pos, image, alpha=120):
        self.pos = list(pos)
        self.image = image.copy()
        self.alpha = alpha
        self.fade_speed = 8

    def update(self):
        self.alpha -= self.fade_speed
        return self.alpha > 0

    def draw(self, surface, camera_offset):
        img = self.image.copy()
        img.set_alpha(max(0, self.alpha))
        surface.blit(img, (self.pos[0] - camera_offset[0] - img.get_width()//2,
                           self.pos[1] - camera_offset[1] - img.get_height()//2))

class Player:
    def __init__(self, x, y):
        self.pos = [float(x), float(y)]
        self.vel = [0.0, 0.0]
        self.max_speed = 220
        self.accel = 900
        self.friction = 0.82
        self.width = 28
        self.height = 28
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)

        self.hp = 100
        self.max_hp = 100
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 0.5

        self.dash_speed = 600
        self.dash_duration = 0.15
        self.dash_cooldown = 1.2
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dashing = False
        self.dash_dir = [0, 0]
        self.afterimages = []

        self.melee_cooldown = 0.5
        self.melee_timer = 0
        self.melee_active = False
        self.melee_duration = 0.12
        self.melee_anim_timer = 0
        self.melee_range = 55
        self.melee_damage = 30
        self.melee_angle = 0

        self.angle = 0
        self.score = 0
        self.coins = 0
        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 3.0
        self.kills = 0

        self.current_weapon_index = 0
        self.weapons = []
        self.secondary_index = 0
        self.secondaries = []

        self.surface = pygame.Surface((28, 28), pygame.SRCALPHA)
        self._draw_player_surface()

        self.alive = True
        self.kill_feed = []
        self.kill_feed_timer = []

    def _draw_player_surface(self):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.surface, (80, 180, 255), (14, 14), 12)
        pygame.draw.circle(self.surface, (200, 230, 255), (14, 14), 12, 2)
        pygame.draw.circle(self.surface, (255, 255, 100), (20, 10), 4)

    def take_damage(self, amount):
        if self.invincible or self.dashing:
            return False
        self.hp -= amount
        self.invincible = True
        self.invincible_timer = self.invincible_duration
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def start_dash(self, dx, dy):
        if self.dash_cooldown_timer > 0:
            return False
        if dx == 0 and dy == 0:
            mx, my = pygame.mouse.get_pos()
            cx, cy = pygame.display.get_surface().get_width()//2, pygame.display.get_surface().get_height()//2
            dx, dy = mx - cx, my - cy
        length = math.hypot(dx, dy)
        if length == 0:
            dx, dy = 1, 0
        else:
            dx, dy = dx/length, dy/length
        self.dash_dir = [dx, dy]
        self.dashing = True
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown
        self.invincible = True
        self.invincible_timer = self.dash_duration + 0.05
        return True

    def do_melee(self, mx, my, camera_offset):
        if self.melee_timer > 0:
            return False
        wx = mx + camera_offset[0]
        wy = my + camera_offset[1]
        self.melee_angle = math.atan2(wy - self.pos[1], wx - self.pos[0])
        self.melee_active = True
        self.melee_anim_timer = self.melee_duration
        self.melee_timer = self.melee_cooldown
        return True

    def get_melee_rect(self):
        if not self.melee_active:
            return None
        cx = self.pos[0] + math.cos(self.melee_angle) * (self.melee_range * 0.5)
        cy = self.pos[1] + math.sin(self.melee_angle) * (self.melee_range * 0.5)
        return pygame.Rect(cx - 20, cy - 20, 40, 40)

    def add_kill(self, enemy_name, coins=5, score=100):
        self.kills += 1
        self.coins += coins
        self.combo += 1
        self.combo_timer = self.combo_timeout
        multiplier = 1 + (self.combo // 5) * 0.5
        self.score += int(score * multiplier)
        self.kill_feed.append(enemy_name)
        self.kill_feed_timer.append(3.0)

    def update(self, dt, keys, walls, hazards=None):
        dx = dy = 0
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1

        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False
                self.dash_timer = 0
            else:
                self.vel[0] = self.dash_dir[0] * self.dash_speed
                self.vel[1] = self.dash_dir[1] * self.dash_speed
                img = self.surface.copy()
                self.afterimages.append(Afterimage(list(self.pos), img))
        else:
            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                dx /= length
                dy /= length
                self.vel[0] += dx * self.accel * dt
                self.vel[1] += dy * self.accel * dt
                speed = math.hypot(self.vel[0], self.vel[1])
                if speed > self.max_speed:
                    scale = self.max_speed / speed
                    self.vel[0] *= scale
                    self.vel[1] *= scale
            self.vel[0] *= (self.friction ** (dt * 60))
            self.vel[1] *= (self.friction ** (dt * 60))

        new_x = self.pos[0] + self.vel[0] * dt
        new_y = self.pos[1] + self.vel[1] * dt

        test_rect_x = pygame.Rect(new_x - 14, self.pos[1] - 14, 28, 28)
        blocked_x = False
        for wall in walls:
            if test_rect_x.colliderect(wall):
                blocked_x = True
                self.vel[0] = 0
                break
        if not blocked_x:
            self.pos[0] = new_x

        test_rect_y = pygame.Rect(self.pos[0] - 14, new_y - 14, 28, 28)
        blocked_y = False
        for wall in walls:
            if test_rect_y.colliderect(wall):
                blocked_y = True
                self.vel[1] = 0
                break
        if not blocked_y:
            self.pos[1] = new_y

        self.rect = pygame.Rect(self.pos[0]-14, self.pos[1]-14, 28, 28)

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        if self.melee_timer > 0:
            self.melee_timer -= dt
        if self.melee_anim_timer > 0:
            self.melee_anim_timer -= dt
            if self.melee_anim_timer <= 0:
                self.melee_active = False

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        self.afterimages = [a for a in self.afterimages if a.update()]

        for i in range(len(self.kill_feed_timer)-1, -1, -1):
            self.kill_feed_timer[i] -= dt
            if self.kill_feed_timer[i] <= 0:
                self.kill_feed.pop(i)
                self.kill_feed_timer.pop(i)

        if hazards:
            for hz in hazards:
                if self.rect.colliderect(hz.rect) and not self.invincible:
                    if hz.apply(self):
                        pass

        mx, my = pygame.mouse.get_pos()
        screen = pygame.display.get_surface()
        cx, cy = screen.get_width()//2, screen.get_height()//2
        self.angle = math.atan2(my - cy, mx - cx)

        if self.weapons:
            self.weapons[self.current_weapon_index].update(dt)

    def draw(self, surface, camera_offset):
        for ai in self.afterimages:
            ai.draw(surface, camera_offset)

        sx = self.pos[0] - camera_offset[0]
        sy = self.pos[1] - camera_offset[1]

        if self.invincible and not self.dashing:
            if int(pygame.time.get_ticks() / 80) % 2 == 0:
                pass
            else:
                rotated = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
                surface.blit(rotated, (sx - rotated.get_width()//2, sy - rotated.get_height()//2))
                return

        rotated = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        surface.blit(rotated, (sx - rotated.get_width()//2, sy - rotated.get_height()//2))

        if self.melee_active:
            arc_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.arc(arc_surf, (255, 200, 50, 180),
                           pygame.Rect(10, 10, 100, 100),
                           self.melee_angle - 0.7, self.melee_angle + 0.7, 8)
            surface.blit(arc_surf, (sx - 60, sy - 60))