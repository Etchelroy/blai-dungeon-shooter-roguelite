import pygame
import math
import random
from settings import *
from weapons import Weapon, Projectile
from abilities import create_ability

PLAYER_SPEED = 220.0
DASH_SPEED = 600.0
DASH_DURATION = 0.15
DASH_COOLDOWN = 0.8
MELEE_COOLDOWN = 0.5
MELEE_DAMAGE = 35
MELEE_RANGE = 70

class Afterimage:
    def __init__(self, x, y, angle, alpha=180):
        self.x = x
        self.y = y
        self.angle = angle
        self.alpha = alpha
        self.lifetime = 0.2

    def update(self, dt):
        self.lifetime -= dt
        self.alpha = int(180 * (self.lifetime / 0.2))

    def render(self, screen, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        draw_player_sprite(s, 16, 16, 0, alpha=self.alpha, color=(100, 180, 255))
        screen.blit(s, (int(sx) - 16, int(sy) - 16))


def draw_player_sprite(surf, cx, cy, angle, alpha=255, color=(80, 160, 240)):
    body_color = color
    dark = tuple(max(0, c - 40) for c in color)
    # Body
    pygame.draw.ellipse(surf, body_color, (cx - 10, cy - 12, 20, 22))
    pygame.draw.ellipse(surf, dark, (cx - 10, cy - 12, 20, 22), 2)
    # Head
    pygame.draw.circle(surf, (220, 190, 150), (cx, cy - 10), 7)
    # Gun direction indicator
    gx = cx + math.cos(angle) * 14
    gy = cy + math.sin(angle) * 14
    pygame.draw.line(surf, (200, 200, 200), (cx, cy), (int(gx), int(gy)), 3)
    pygame.draw.circle(surf, (160, 160, 180), (int(gx), int(gy)), 3)

# filename: enemies.py
```python
import pygame, math, random
from settings import *
from particles import ParticleSystem
from utils import distance, angle_to, normalize

class BaseEnemy:
    def __init__(self, x, y, ps: ParticleSystem):
        self.x = x; self.y = y
        self.ps = ps
        self.vx = 0; self.vy = 0
        self.hp = 10; self.max_hp = 10
        self.speed = 60
        self.radius = 8
        self.alive = True
        self.phase = 0
        self.damage = 8
        self.score_value = 100
        self.coin_value = 1
        self.tier = 1
        self.anim_timer = 0
        self.flash_timer = 0
        self.status_effects = {}  # 'burn','freeze','poison'
        self.knockback_vx = 0; self.knockback_vy = 0
        self.attack_cooldown = 0
        self.facing = 1
        self.color = (180, 60, 60)
        self.acc_x = 0; self.acc_y = 0

    def take_damage(self, amount, kx=0, ky=0):
        self.hp -= amount
        self.flash_timer = 0.1
        self.knockback_vx += kx * 3
        self.knockback_vy += ky * 3
        if self.hp <= 0:
            self.die()
            return True
        return False

    def die(self):
        self.alive = False
        for _ in range(12):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(40, 120)
            self.ps.emit(self.x, self.y, math.cos(angle)*speed, math.sin(angle)*speed,
                         self.color, random.uniform(0.3, 0.8), random.randint(2, 5))

    def apply_status(self, status, duration, value=0):
        self.status_effects[status] = {'duration': duration, 'value': value, 'timer': 0}

    def update_status(self, dt):
        for s in list(self.status_effects.keys()):
            data = self.status_effects[s]
            data['timer'] += dt
            if data['timer'] >= data['duration']:
                del self.status_effects[s]
                continue
            if s == 'burn' and int(data['timer'] * 10) != int((data['timer'] - dt) * 10):
                self.hp -= data['value']
                self.ps.emit(self.x, self.y, random.uniform(-20, 20), random.uniform(-40, -10),
                             (255, 150, 30), 0.3, 3)
                if self.hp <= 0:
                    self.alive = False
            if s == 'freeze':
                pass
            if s == 'poison' and int(data['timer'] * 5) != int((data['timer'] - dt) * 5):
                self.hp -= data['value']
                self.ps.emit(self.x, self.y, random.uniform(-10, 10), random.uniform(-10, 10),
                             (80, 200, 80), 0.4, 2)
                if self.hp <= 0:
                    self.alive = False

    def move_toward_player(self, px, py, dt, speed_mult=1.0):
        dx = px - self.x; dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            speed = self.speed * speed_mult
            if 'freeze' in self.status_effects:
                speed *= 0.3
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed

    def update(self, dt, player, tilemap, spatial_hash):
        self.anim_timer += dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.update_status(dt)
        self.knockback_vx *= (1 - 10 * dt)
        self.knockback_vy *= (1 - 10 * dt)
        self.x += (self.vx + self.knockback_vx) * dt
        self.y += (self.vy + self.knockback_vy) * dt
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        if self.x - self.radius < 0: self.x = self.radius
        if self.y - self.radius < 0: self.y = self.radius

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (int(sx), int(sy)), self.radius)
        bar_w = 30
        bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 8, int(bar_w * ratio), bar_h))

    def get_draw_order(self):
        return self.y


class Slime(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 25
        self.speed = 55
        self.color = (80, 200, 100)
        self.radius = 9
        self.score_value = 50
        self.coin_value = 1
        self.bounce_timer = 0
        self.damage = 6

    def update(self, dt, player, tilemap, spatial_hash):
        self.bounce_timer += dt
        self.move_toward_player(player.x, player.y, dt)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        squish = 1 + 0.15 * math.sin(self.bounce_timer * 8)
        w = int(self.radius * 2 * squish)
        h = int(self.radius * 2 / squish)
        rect = pygame.Rect(sx - w//2, sy - h//2, w, h)
        pygame.draw.ellipse(surf, col, rect)
        eye_off = int(3 * squish)
        pygame.draw.circle(surf, (20, 20, 20), (sx - eye_off, sy - 2), 2)
        pygame.draw.circle(surf, (20, 20, 20), (sx + eye_off, sy - 2), 2)
        bar_w = 30; bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 8, int(bar_w * ratio), bar_h))


class Goblin(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 40
        self.speed = 85
        self.color = (120, 180, 60)
        self.radius = 7
        self.score_value = 100
        self.coin_value = 2
        self.charge_timer = 0
        self.charging = False
        self.charge_vx = 0; self.charge_vy = 0
        self.damage = 10
        self.tier = 1

    def update(self, dt, player, tilemap, spatial_hash):
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if not self.charging:
            if dist < 200 and self.attack_cooldown <= 0:
                self.charging = True
                self.charge_timer = 0.4
                if dist > 0:
                    self.charge_vx = dx/dist * 300
                    self.charge_vy = dy/dist * 300
                self.attack_cooldown = 2.0
            else:
                self.move_toward_player(player.x, player.y, dt)
        else:
            self.charge_timer -= dt
            self.vx = self.charge_vx
            self.vy = self.charge_vy
            if self.charge_timer <= 0:
                self.charging = False
                self.vx = 0; self.vy = 0
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pts = [
            (sx, sy - self.radius - 4),
            (sx + self.radius, sy + self.radius),
            (sx - self.radius, sy + self.radius)
        ]
        pygame.draw.polygon(surf, col, pts)
        if self.charging:
            pygame.draw.polygon(surf, (255, 200, 0), pts, 2)
        bar_w = 30; bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 12, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 12, int(bar_w * ratio), bar_h))


class Skeleton(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 35
        self.speed = 50
        self.color = (220, 220, 200)
        self.radius = 8
        self.score_value = 120
        self.coin_value = 2
        self.shoot_cooldown = 0
        self.bone_projectiles = []
        self.damage = 8
        self.tier = 1

    def update(self, dt, player, tilemap, spatial_hash):
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 150:
            self.move_toward_player(player.x, player.y, dt)
        else:
            self.vx *= 0.9; self.vy *= 0.9
        self.shoot_cooldown -= dt
        if self.shoot_cooldown <= 0 and dist < 300:
            self.shoot_cooldown = 1.5
            if dist > 0:
                speed = 150
                self.bone_projectiles.append({
                    'x': self.x, 'y': self.y,
                    'vx': dx/dist*speed, 'vy': dy/dist*speed,
                    'life': 2.0
                })
        for p in self.bone_projectiles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.bone_projectiles.remove(p)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (sx, sy - 4), 6)
        pygame.draw.rect(surf, col, (sx - 5, sy + 2, 10, 8))
        pygame.draw.line(surf, col, (sx - 5, sy + 10), (sx - 5, sy + 16), 2)
        pygame.draw.line(surf, col, (sx + 5, sy + 10), (sx + 5, sy + 16), 2)
        for p in self.bone_projectiles:
            bx, by = cam.world_to_screen(p['x'], p['y'])
            pygame.draw.circle(surf, (240, 230, 200), (int(bx), int(by)), 3)
        bar_w = 30; bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 8, int(bar_w * ratio), bar_h))


class Bat(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 20
        self.speed = 110
        self.color = (100, 60, 140)
        self.radius = 6
        self.score_value = 80
        self.coin_value = 1
        self.wobble = random.uniform(0, math.tau)
        self.damage = 5
        self.tier = 1

    def update(self, dt, player, tilemap, spatial_hash):
        self.wobble += dt * 4
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.vx = dx/dist * self.speed + math.cos(self.wobble) * 40
            self.vy = dy/dist * self.speed + math.sin(self.wobble) * 40
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        wing_flap = math.sin(self.anim_timer * 15) * 6
        pygame.draw.ellipse(surf, col, (sx - 12, sy - 3 + int(wing_flap), 10, 8))
        pygame.draw.ellipse(surf, col, (sx + 2, sy - 3 - int(wing_flap), 10, 8))
        pygame.draw.circle(surf, col, (sx, sy), 5)
        pygame.draw.circle(surf, (255, 50, 50), (sx - 2, sy - 1), 1)
        pygame.draw.circle(surf, (255, 50, 50), (sx + 2, sy - 1), 1)
        bar_w = 24; bar_h = 3
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 8, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 8, int(bar_w * ratio), bar_h))


class Orc(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 120
        self.speed = 45
        self.color = (60, 140, 60)
        self.radius = 14
        self.score_value = 200
        self.coin_value = 4
        self.damage = 20
        self.tier = 2
        self.slam_timer = 0
        self.slamming = False

    def update(self, dt, player, tilemap, spatial_hash):
        self.move_toward_player(player.x, player.y, dt)
        if not self.slamming and self.attack_cooldown <= 0:
            dist = distance(self.x, self.y, player.x, player.y)
            if dist < 60:
                self.slamming = True
                self.slam_timer = 0.5
                self.attack_cooldown = 2.5
        if self.slamming:
            self.slam_timer -= dt
            if self.slam_timer <= 0:
                self.slamming = False
                for _ in range(8):
                    a = random.uniform(0, math.tau)
                    self.ps.emit(self.x, self.y, math.cos(a)*80, math.sin(a)*80, (100, 80, 40), 0.5, 5)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        if self.slamming:
            col = (255, 180, 0)
        pygame.draw.rect(surf, col, (sx - self.radius, sy - self.radius, self.radius*2, self.radius*2))
        pygame.draw.circle(surf, col, (sx, sy - self.radius - 5), 8)
        pygame.draw.circle(surf, (255, 200, 150), (sx, sy - self.radius - 5), 6)
        pygame.draw.line(surf, (80, 60, 20), (sx - self.radius - 4, sy), (sx - self.radius - 4, sy + 12), 3)
        bar_w = 40; bar_h = 5
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 10, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 10, int(bar_w * ratio), bar_h))


class Mage(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 70
        self.speed = 40
        self.color = (160, 80, 200)
        self.radius = 9
        self.score_value = 250
        self.coin_value = 5
        self.damage = 15
        self.tier = 2
        self.teleport_cooldown = 5.0
        self.projectiles = []
        self.shoot_cooldown = 0

    def update(self, dt, player, tilemap, spatial_hash):
        dist = distance(self.x, self.y, player.x, player.y)
        if dist < 120 or dist > 350:
            dx = player.x - self.x; dy = player.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                direction = -1 if dist < 120 else 1
                self.vx = dx/d * self.speed * direction
                self.vy = dy/d * self.speed * direction
        else:
            self.vx *= 0.9; self.vy *= 0.9
        self.teleport_cooldown -= dt
        if self.teleport_cooldown <= 0:
            self.teleport_cooldown = 5.0
            angle = random.uniform(0, math.tau)
            r = random.uniform(150, 250)
            self.x = player.x + math.cos(angle) * r
            self.y = player.y + math.sin(angle) * r
            for _ in range(10):
                a = random.uniform(0, math.tau)
                self.ps.emit(self.x, self.y, math.cos(a)*60, math.sin(a)*60, (160, 80, 200), 0.5, 4)
        self.shoot_cooldown -= dt
        if self.shoot_cooldown <= 0 and dist < 400:
            self.shoot_cooldown = 1.0
            dx = player.x - self.x; dy = player.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                for spread in [-0.2, 0, 0.2]:
                    angle = math.atan2(dy, dx) + spread
                    speed = 180
                    self.projectiles.append({
                        'x': self.x, 'y': self.y,
                        'vx': math.cos(angle)*speed,
                        'vy': math.sin(angle)*speed,
                        'life': 2.5
                    })
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            self.ps.emit(p['x'], p['y'], 0, 0, (160, 80, 200), 0.1, 2)
            if p['life'] <= 0:
                self.projectiles.remove(p)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (sx, sy), self.radius)
        hat_pts = [(sx, sy - self.radius - 12), (sx - 8, sy - self.radius), (sx + 8, sy - self.radius)]
        pygame.draw.polygon(surf, (80, 20, 120), hat_pts)
        pygame.draw.circle(surf, (220, 180, 255), (sx, sy - self.radius - 14), 3)
        for p in self.projectiles:
            px, py = cam.world_to_screen(p['x'], p['y'])
            pygame.draw.circle(surf, (200, 100, 255), (int(px), int(py)), 5)
            pygame.draw.circle(surf, (255, 200, 255), (int(px), int(py)), 2)
        bar_w = 34; bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 10, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 10, int(bar_w * ratio), bar_h))


class Troll(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 200
        self.speed = 35
        self.color = (80, 120, 60)
        self.radius = 18
        self.score_value = 400
        self.coin_value = 8
        self.damage = 25
        self.tier = 2
        self.regen_timer = 0

    def update(self, dt, player, tilemap, spatial_hash):
        self.move_toward_player(player.x, player.y, dt)
        self.regen_timer += dt
        if self.regen_timer >= 1.0:
            self.regen_timer = 0
            if self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 3)
                self.ps.emit(self.x, self.y, 0, -30, (80, 200, 80), 0.4, 3)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (sx, sy), self.radius)
        pygame.draw.circle(surf, (60, 90, 40), (sx, sy), self.radius, 3)
        pygame.draw.circle(surf, (200, 160, 120), (sx, sy - 4), 10)
        pygame.draw.circle(surf, (40, 30, 20), (sx - 3, sy - 5), 2)
        pygame.draw.circle(surf, (40, 30, 20), (sx + 3, sy - 5), 2)
        bar_w = 50; bar_h = 6
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 12, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 12, int(bar_w * ratio), bar_h))


class Ghost(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 50
        self.speed = 70
        self.color = (180, 200, 255)
        self.radius = 10
        self.score_value = 300
        self.coin_value = 6
        self.damage = 12
        self.tier = 2
        self.alpha = 128
        self.phase_timer = random.uniform(0, math.tau)
        self.tangible = True
        self.intangible_timer = 0

    def update(self, dt, player, tilemap, spatial_hash):
        self.phase_timer += dt * 2
        self.alpha = int(128 + 80 * math.sin(self.phase_timer))
        self.intangible_timer -= dt
        if self.intangible_timer <= 0:
            dist = distance(self.x, self.y, player.x, player.y)
            if dist < 80 and self.attack_cooldown <= 0:
                self.intangible_timer = 2.0
                self.tangible = False
                self.attack_cooldown = 3.0
            else:
                self.tangible = True
        else:
            self.tangible = self.intangible_timer < 1.0
        self.move_toward_player(player.x, player.y, dt)
        super().update(dt, player, tilemap, spatial_hash)

    def take_damage(self, amount, kx=0, ky=0):
        if not self.tangible:
            return False
        return super().take_damage(amount, kx, ky)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        ghost_surf = pygame.Surface((self.radius*2+4, self.radius*2+8), pygame.SRCALPHA)
        alpha = self.alpha if self.tangible else self.alpha // 2
        pygame.draw.circle(ghost_surf, (*col, alpha), (self.radius+2, self.radius+2), self.radius)
        pts = [(2, self.radius+2), (self.radius*2+2, self.radius+2),
               (self.radius*2+2, self.radius*2+6), (int(self.radius*1.5)+2, self.radius*2+2),
               (self.radius+2, self.radius*2+6), (int(self.radius*0.5)+2, self.radius*2+2),
               (2, self.radius*2+6)]
        pygame.draw.polygon(ghost_surf, (*col, alpha), pts)
        pygame.draw.circle(ghost_surf, (20, 20, 80, alpha), (self.radius-2, self.radius), 3)
        pygame.draw.circle(ghost_surf, (20, 20, 80, alpha), (self.radius+4, self.radius), 3)
        surf.blit(ghost_surf, (sx - self.radius - 2, sy - self.radius - 2))
        bar_w = 34; bar_h = 4
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 12, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 12, int(bar_w * ratio), bar_h))


class Demon(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 150
        self.speed = 90
        self.color = (200, 40, 40)
        self.radius = 12
        self.score_value = 500
        self.coin_value = 10
        self.damage = 18
        self.tier = 3
        self.dash_cooldown = 3.0
        self.dashing = False
        self.dash_timer = 0
        self.dash_vx = 0; self.dash_vy = 0
        self.projectiles = []
        self.shoot_cooldown = 0

    def update(self, dt, player, tilemap, spatial_hash):
        self.shoot_cooldown -= dt
        self.dash_cooldown -= dt
        dist = distance(self.x, self.y, player.x, player.y)
        if self.dash_cooldown <= 0 and dist < 300:
            self.dash_cooldown = 3.0
            self.dashing = True
            self.dash_timer = 0.3
            dx = player.x - self.x; dy = player.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                self.dash_vx = dx/d * 400
                self.dash_vy = dy/d * 400
        if self.dashing:
            self.dash_timer -= dt
            self.vx = self.dash_vx
            self.vy = self.dash_vy
            for _ in range(2):
                self.ps.emit(self.x, self.y, random.uniform(-20, 20), random.uniform(-20, 20),
                             (255, 80, 20), 0.2, 4)
            if self.dash_timer <= 0:
                self.dashing = False
                self.vx = 0; self.vy = 0
        else:
            self.move_toward_player(player.x, player.y, dt)
        if self.shoot_cooldown <= 0 and dist < 350:
            self.shoot_cooldown = 0.8
            angle = angle_to(self.x, self.y, player.x, player.y)
            for a in [angle - 0.3, angle, angle + 0.3]:
                self.projectiles.append({'x': self.x, 'y': self.y,
                                          'vx': math.cos(a)*200, 'vy': math.sin(a)*200, 'life': 2.0})
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.projectiles.remove(p)
        super().update(dt, player, tilemap, spatial_hash)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (sx, sy), self.radius)
        for i, (ox, oy) in enumerate([(-self.radius-2, -4), (self.radius+2, -4)]):
            pts = [(sx+ox, sy+oy), (sx+ox-4*(-1 if i==0 else 1), sy+oy-10),
                   (sx+ox+4*(-1 if i==0 else 1), sy+oy-10)]
            pygame.draw.polygon(surf, (220, 20, 20), pts)
        pygame.draw.line(surf, (60, 20, 10), (sx-4, sy+self.radius), (sx-4, sy+self.radius+8), 2)
        pygame.draw.line(surf, (60, 20, 10), (sx+4, sy+self.radius), (sx+4, sy+self.radius+8), 2)
        for p in self.projectiles:
            px, py = cam.world_to_screen(p['x'], p['y'])
            pygame.draw.circle(surf, (255, 80, 20), (int(px), int(py)), 4)
        bar_w = 40; bar_h = 5
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 12, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 12, int(bar_w * ratio), bar_h))


class Warlock(BaseEnemy):
    def __init__(self, x, y, ps):
        super().__init__(x, y, ps)
        self.hp = self.max_hp = 180
        self.speed = 30
        self.color = (80, 20, 120)
        self.radius = 11
        self.score_value = 600
        self.coin_value = 12
        self.damage = 20
        self.tier = 3
        self.summon_cooldown = 8.0
        self.shield_hp = 30
        self.shield_max = 30
        self.shield_regen = 0
        self.projectiles = []
        self.shoot_cooldown = 0
        self.summons = []

    def update(self, dt, player, tilemap, spatial_hash):
        self.summon_cooldown -= dt
        self.shoot_cooldown -= dt
        self.shield_regen += dt
        if self.shield_regen >= 3.0 and self.shield_hp < self.shield_max:
            self.shield_hp = min(self.shield_max, self.shield_hp + 5)
            self.shield_regen = 0
        dist = distance(self.x, self.y, player.x, player.y)
        if dist < 200:
            dx = player.x - self.x; dy = player.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                self.vx = -dx/d * self.speed
                self.vy = -dy/d * self.speed
        else:
            self.vx *= 0.8; self.vy *= 0.8
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 0.5
            angle = angle_to(self.x, self.y, player.x, player.y)
            self.projectiles.append({'x': self.x, 'y': self.y,
                                      'vx': math.cos(angle)*160, 'vy': math.sin(angle)*160,
                                      'life': 3.0, 'homing': True})
        for p in self.projectiles[:]:
            if p.get('homing'):
                dx = player.x - p['x']; dy = player.y - p['y']
                d = math.hypot(dx, dy)
                if d > 0:
                    p['vx'] += dx/d * 200 * dt
                    p['vy'] += dy/d * 200 * dt
                    speed = math.hypot(p['vx'], p['vy'])
                    if speed > 200:
                        p['vx'] = p['vx']/speed*200
                        p['vy'] = p['vy']/speed*200
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            self.ps.emit(p['x'], p['y'], 0, 0, (120, 40, 180), 0.15, 3)
            if p['life'] <= 0:
                self.projectiles.remove(p)
        super().update(dt, player, tilemap, spatial_hash)

    def take_damage(self, amount, kx=0, ky=0):
        if self.shield_hp > 0:
            self.shield_hp -= amount
            self.shield_regen = 0
            for _ in range(4):
                a = random.uniform(0, math.tau)
                self.ps.emit(self.x, self.y, math.cos(a)*40, math.sin(a)*40, (140, 80, 220), 0.3, 3)
            if self.shield_hp <= 0:
                self.shield_hp = 0
            return False
        return super().take_damage(amount, kx, ky)

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (sx, sy), self.radius)
        if self.shield_hp > 0:
            ratio = self.shield_hp / self.shield_max
            shield_col = (int(80 + 100*ratio), int(20 + 80*ratio), int(220))
            pygame.draw.circle(surf, shield_col, (sx, sy), self.radius + 4, 2)
        pygame.draw.circle(surf, (150, 100, 200), (sx, sy - 5), 6)
        pygame.draw.circle(surf, (220, 180, 255), (sx - 2, sy - 6), 2)
        pygame.draw.circle(surf, (220, 180, 255), (sx + 2, sy - 6), 2)
        for p in self.projectiles:
            px, py = cam.world_to_screen(p['x'], p['y'])
            pygame.draw.circle(surf, (160, 60, 220), (int(px), int(py)), 5)
            pygame.draw.circle(surf, (220, 180, 255), (int(px), int(py)), 2)
        bar_w = 44; bar_h = 5
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (80, 0, 0), (sx - bar_w//2, sy - self.radius - 12, bar_w, bar_h))
        pygame.draw.rect(surf, (200, 50, 50), (sx - bar_w//2, sy - self.radius - 12, int(bar_w * ratio), bar_h))


ENEMY_TYPES = {
    'slime': Slime,
    'goblin': Goblin,
    'skeleton': Skeleton,
    'bat': Bat,
    'orc': Orc,
    'mage': Mage,
    'troll': Troll,
    'ghost': Ghost,
    'demon': Demon,
    'warlock': Warlock,
}

TIER_ENEMIES = {
    1: ['slime', 'goblin', 'skeleton', 'bat'],
    2: ['orc', 'mage', 'ghost', 'troll'],
    3: ['demon', 'warlock'],
}