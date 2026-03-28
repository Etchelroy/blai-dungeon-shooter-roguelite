import pygame
import math
import random
from settings import *
from assets import make_bullet_sprite
from utils import normalize, angle_to, vec_from_angle

class Bullet:
    def __init__(self, x, y, vx, vy, damage, wtype, owner='player', pierce=False, aoe=False, aoe_r=0, lifetime=2.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.wtype = wtype
        self.owner = owner
        self.pierce = pierce
        self.aoe = aoe
        self.aoe_r = aoe_r
        self.lifetime = lifetime
        self.alive = True
        self.hit_set = set()
        self.sprite = make_bullet_sprite(wtype)
        self.angle = math.degrees(math.atan2(vy, vx))
        self.chain_count = 0
        self.max_chain = 0
        # Boomerang
        self.returning = False
        self.owner_ref = None
        # Flamethrower DoT
        self.is_dot = False
        self.dot_dmg = 0
        self.dot_dur = 0

    def update(self, dt, arena=None, player=None):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        # Boomerang return
        if self.returning and player:
            tx, ty = player.x, player.y
            dx, dy = normalize(tx-self.x, ty-self.y)
            self.vx = dx*500
            self.vy = dy*500
            if math.hypot(tx-self.x, ty-self.y) < 20:
                self.alive = False
                return
        # Wall collision
        if arena:
            col, row = int(self.x//TILE_PX), int(self.y//TILE_PX)
            if arena.tilemap.is_solid(col, row):
                if self.aoe:
                    self.alive = False
                    return
                if not self.pierce:
                    self.alive = False
                    return
        # Crate collision
        if arena:
            for crate in arena.crates:
                if crate.alive and crate.rect.collidepoint(self.x, self.y):
                    crate.take_damage(self.damage)
                    if not self.pierce:
                        self.alive = False
                    return

    def draw(self, surface, cam_ox, cam_oy):
        if not self.alive: return
        sx = int(self.x - cam_ox)
        sy = int
# filename: abilities.py
```python
import pygame
import math
import random
from settings import *

class Ability:
    def __init__(self, name, cooldown):
        self.name = name
        self.cooldown = cooldown
        self.timer = 0
        self.active = False
        self.duration = 0
        self.duration_timer = 0

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
        if self.active and self.duration > 0:
            self.duration_timer -= dt
            if self.duration_timer <= 0:
                self.active = False

    def can_use(self):
        return self.timer <= 0

    def use(self):
        self.timer = self.cooldown
        self.active = True
        self.duration_timer = self.duration

    def get_cooldown_ratio(self):
        return max(0, self.timer / self.cooldown) if self.cooldown > 0 else 0


class ShieldAbility(Ability):
    def __init__(self):
        super().__init__("Shield", 8.0)
        self.duration = 3.0
        self.block_damage = True

    def activate(self, player, particles, effects):
        if not self.can_use():
            return False
        self.use()
        effects.screen_flash((100, 150, 255), 0.2)
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            particles.emit('spark', player.pos[0] + math.cos(angle) * 30,
                          player.pos[1] + math.sin(angle) * 30,
                          count=1, color=(100, 150, 255))
        return True


class TimeWarpAbility(Ability):
    def __init__(self):
        super().__init__("TimeWarp", 15.0)
        self.duration = 5.0
        self.slow_factor = 0.3

    def activate(self, player, particles, effects):
        if not self.can_use():
            return False
        self.use()
        effects.set_slow_mo(self.slow_factor, self.duration)
        effects.screen_flash((200, 100, 255), 0.3)
        return True


class NovaBombAbility(Ability):
    def __init__(self):
        super().__init__("NovaBomb", 12.0)
        self.radius = 200
        self.damage = 80

    def activate(self, player, particles, effects):
        if not self.can_use():
            return False
        self.use()
        effects.screen_shake(15, 0.5)
        effects.screen_flash((255, 200, 50), 0.4)
        for i in range(60):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0, self.radius)
            particles.emit('explosion', player.pos[0] + math.cos(angle) * dist,
                          player.pos[1] + math.sin(angle) * dist, count=3)
        return True

    def get_affected_enemies(self, player, enemies):
        affected = []
        for e in enemies:
            dx = e.pos[0] - player.pos[0]
            dy = e.pos[1] - player.pos[1]
            if math.sqrt(dx*dx + dy*dy) <= self.radius:
                affected.append(e)
        return affected


class TeleportAbility(Ability):
    def __init__(self):
        super().__init__("Teleport", 10.0)

    def activate(self, player, particles, effects, target_pos=None):
        if not self.can_use():
            return False
        old_pos = player.pos[:]
        self.use()
        if target_pos:
            player.pos[0] = target_pos[0]
            player.pos[1] = target_pos[1]
        else:
            mx, my = pygame.mouse.get_pos()
            cam_x = player.pos[0] - VIEWPORT_W // 2
            cam_y = player.pos[1] - VIEWPORT_H // 2
            player.pos[0] = mx + cam_x
            player.pos[1] = my + cam_y
        for i in range(30):
            particles.emit('spark', old_pos[0], old_pos[1], count=1,
                          color=(150, 50, 255))
        for i in range(30):
            particles.emit('spark', player.pos[0], player.pos[1], count=1,
                          color=(150, 50, 255))
        effects.screen_flash((150, 50, 255), 0.15)
        return True


class AdrenalineAbility(Ability):
    def __init__(self):
        super().__init__("Adrenaline", 20.0)
        self.duration = 8.0
        self.speed_mult = 2.0
        self.damage_mult = 1.5

    def activate(self, player, particles, effects):
        if not self.can_use():
            return False
        self.use()
        effects.screen_flash((255, 50, 50), 0.2)
        for i in range(40):
            angle = random.uniform(0, math.pi * 2)
            particles.emit('spark', player.pos[0], player.pos[1], count=1,
                          color=(255, 100, 0))
        return True


class SentryAbility(Ability):
    def __init__(self):
        super().__init__("Sentry", 18.0)
        self.duration = 10.0
        self.sentries = []
        self.sentry_damage = 15
        self.sentry_fire_rate = 0.5

    def activate(self, player, particles, effects):
        if not self.can_use():
            return False
        self.use()
        self.sentries = []
        for i in range(3):
            angle = (i / 3) * math.pi * 2
            sx = player.pos[0] + math.cos(angle) * 60
            sy = player.pos[1] + math.sin(angle) * 60
            self.sentries.append({
                'pos': [sx, sy],
                'angle': angle,
                'fire_timer': 0,
                'orbit_angle': angle
            })
        effects.screen_flash((50, 255, 150), 0.2)
        return True

    def update_sentries(self, dt, player, enemies, bullets, particles):
        if not self.active:
            self.sentries = []
            return
        for s in self.sentries:
            s['orbit_angle'] += dt * 2.0
            s['pos'][0] = player.pos[0] + math.cos(s['orbit_angle']) * 60
            s['pos'][1] = player.pos[1] + math.sin(s['orbit_angle']) * 60
            s['fire_timer'] -= dt
            if s['fire_timer'] <= 0 and enemies:
                s['fire_timer'] = self.sentry_fire_rate
                nearest = min(enemies, key=lambda e: (e.pos[0]-s['pos'][0])**2 + (e.pos[1]-s['pos'][1])**2)
                dx = nearest.pos[0] - s['pos'][0]
                dy = nearest.pos[1] - s['pos[1]'] if '1' in str(s) else nearest.pos[1] - s['pos'][1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0 and dist < 300:
                    bullets.append({
                        'pos': [s['pos'][0], s['pos'][1]],
                        'vel': [dx/dist * 400, dy/dist * 400],
                        'damage': self.sentry_damage,
                        'owner': 'sentry',
                        'life': 1.0,
                        'radius': 4
                    })


ABILITIES = {
    'shield': ShieldAbility,
    'timewarp': TimeWarpAbility,
    'nova': NovaBombAbility,
    'teleport': TeleportAbility,
    'adrenaline': AdrenalineAbility,
    'sentry': SentryAbility,
}

def create_ability(name):
    cls = ABILITIES.get(name)
    if cls:
        return cls()
    return None