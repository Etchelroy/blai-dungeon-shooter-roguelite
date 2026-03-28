import pygame, math, random
from settings import *
from src.utils import clamp, lerp, angle_to, distance

class Entity:
    def __init__(self, x, y, w, h):
        self.x, self.y = float(x), float(y)
        self.w, self.h = w, h
        self.vx, self.vy = 0.0, 0.0
        self.alive = True
        self.rect = pygame.Rect(x, y, w, h)

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_center(self):
        return (self.x + self.w/2, self.y + self.h/2)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 24)
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.speed = PLAYER_SPEED
        self.dash_cd = 0.0
        self.dash_timer = 0.0
        self.dash_dir = (0, 0)
        self.invincible = 0.0
        self.facing = 0.0
        self.coins = 0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.kills = 0
        self.damage_dealt = 0
        self.afterimages = []
        self.flash_timer = 0.0
        self.melee_timer = 0.0
        self.melee_cd = 0.0
        self.upgrades = {}
        self.ammo = {}
        self.active_weapon_idx = 0
        self.weapons = []
        self.secondary = None
        self.secondary_cd = 0.0
        self.walk_anim = 0.0

    def take_damage(self, amt):
        if self.invincible > 0:
            return False
        shield = self.upgrades.get('shield', 0)
        if shield > 0:
            self.upgrades['shield'] = 0
            return False
        self.hp -= amt
        self.invincible = 0.8
        self.flash_timer = 0.2
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def heal(self, amt):
        self.hp = min(self.max_hp, self.hp + amt)

    def add_upgrade(self, key, val=1):
        self.upgrades[key] = self.upgrades.get(key, 0) + val

    def dash(self, dx, dy):
        if self.dash_cd > 0 or self.dash_timer > 0:
            return
        mag = math.sqrt(dx*dx + dy*dy)
        if mag == 0:
            dx, dy = math.cos(self.facing), math.sin(self.facing)
        else:
            dx, dy = dx/mag, dy/mag
        self.dash_dir = (dx, dy)
        self.dash_timer = DASH_DURATION
        self.dash_cd = DASH_COOLDOWN
        self.invincible = DASH_DURATION + 0.1

    def update(self, dt, keys, arena):
        # movement
        move_x, move_y = 0.0, 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_y += 1

        if self.dash_timer > 0:
            self.dash_timer -= dt
            speed = DASH_SPEED
            self.vx = self.dash_dir[0] * speed
            self.vy = self.dash_dir[1] * speed
            # afterimage
            self.afterimages.append({'x': self.x, 'y': self.y, 'alpha': 180, 'facing': self.facing})
        else:
            friction = self.upgrades.get('slick_boots', 0) * 0.05
            fric = max(0.1, FRICTION - friction)
            spd = self.speed * (1 + self.upgrades.get('speed_boost', 0) * 0.15)
            if move_x != 0 or move_y != 0:
                mag = math.sqrt(move_x**2 + move_y**2)
                move_x /= mag; move_y /= mag
                self.vx += move_x * spd * dt * 10
                self.vy += move_y * spd * dt * 10
                self.walk_anim += dt * 8
            self.vx *= fric
            self.vy *= fric

        # timers
        if self.dash_cd > 0: self.dash_cd -= dt
        if self.invincible > 0: self.invincible -= dt
        if self.flash_timer > 0: self.flash_timer -= dt
        if self.melee_cd > 0: self.melee_cd -= dt
        if self.melee_timer > 0: self.melee_timer -= dt
        if self.secondary_cd > 0: self.secondary_cd -= dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        # apply velocity with collision
        self._move(dt, arena)

        # afterimages decay
        for ai in self.afterimages:
            ai['alpha'] -= 300 * dt
        self.afterimages = [a for a in self.afterimages if a['alpha'] > 0]

        self.update_rect()

    def _move(self, dt, arena):
        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt
        # tile collision
        if arena and not arena.is_walkable_rect(pygame.Rect(nx, self.y, self.w, self.h)):
            self.vx = 0; nx = self.x
        if arena and not arena.is_walkable_rect(pygame.Rect(self.x, ny, self.w, self.h)):
            self.vy = 0; ny = self.y
        self.x = clamp(nx, 0, arena.pixel_w - self.w if arena else 9999)
        self.y = clamp(ny, 0, arena.pixel_h - self.h if arena else 9999)

    def add_kill(self, score_val):
        self.kills += 1
        self.combo += 1
        self.combo_timer = COMBO_TIMEOUT
        mult = 1 + self.combo * 0.1
        self.score += int(score_val * mult)

    def draw(self, surf, cam):
        cx, cy = cam.world_to_screen(self.x, self.y)

        # afterimages
        for ai in self.afterimages:
            ax, ay = cam.world_to_screen(ai['x'], ai['y'])
            s = pygame.Surface((24, 24), pygame.SRCALPHA)
            self._draw_sprite(s, 0, 0, ai['facing'], int(ai['alpha']))
            surf.blit(s, (ax, ay))

        # flash effect
        if self.flash_timer > 0 and int(self.flash_timer * 20) % 2 == 0:
            return

        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        self._draw_sprite(s, 0, 0, self.facing, 255)
        surf.blit(s, (cx, cy))

        # melee arc
        if self.melee_timer > 0:
            arc_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            angle_deg = math.degrees(self.facing)
            pygame.draw.arc(arc_surf, (255, 200, 100, 120),
                           (0, 0, 80, 80),
                           math.radians(angle_deg - 45),
                           math.radians(angle_deg + 45), 8)
            surf.blit(arc_surf, (cx - 28, cy - 28))

    def _draw_sprite(self, surf, ox, oy, facing, alpha):
        # body
        color = (100, 180, 255, alpha)
        pygame.draw.rect(surf, color, (ox+4, oy+6, 16, 14))
        # head
        pygame.draw.rect(surf, (220, 180, 140, alpha), (ox+6, oy+1, 12, 10))
        # legs
        leg_offset = int(math.sin(self.walk_anim) * 3)
        pygame.draw.rect(surf, (60, 100, 180, alpha), (ox+5, oy+18, 5, 6+leg_offset))
        pygame.draw.rect(surf, (60, 100, 180, alpha), (ox+14, oy+18, 5, 6-leg_offset))
        # gun direction indicator
        gx = ox + 12 + int(math.cos(facing) * 10)
        gy = oy + 10 + int(math.sin(facing) * 10)
        pygame.draw.line(surf, (200, 200, 200, alpha), (ox+12, oy+10), (gx, gy), 3)