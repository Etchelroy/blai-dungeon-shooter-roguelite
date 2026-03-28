import pygame
import math
import random

class BaseEnemy:
    TIER = 1
    NAME = "Enemy"
    HP = 50
    SPEED = 80
    DAMAGE = 10
    SCORE = 100
    COINS = 3
    COLOR = (200, 80, 80)
    SIZE = 20

    def __init__(self, x, y):
        self.pos = [float(x), float(y)]
        self.hp = self.HP
        self.max_hp = self.HP
        self.alive = True
        self.vel = [0.0, 0.0]
        self.rect = pygame.Rect(x - self.SIZE, y - self.SIZE, self.SIZE*2, self.SIZE*2)
        self.state = "chase"
        self.state_timer = 0
        self.attack_cooldown = 0
        self.attack_rate = 1.5
        self.projectiles = []
        self.flash_timer = 0
        self.death_particles = []
        self.on_death_called = False
        self.status_effects = {}

    def take_damage(self, amount, source=None):
        self.hp -= amount
        self.flash_timer = 0.1
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def apply_status(self, status, duration, value=0):
        self.status_effects[status] = {"timer": duration, "value": value}

    def update_status(self, dt):
        to_remove = []
        for s, data in self.status_effects.items():
            data["timer"] -= dt
            if s == "burn" and data["timer"] > 0:
                pass
            if data["timer"] <= 0:
                to_remove.append(s)
        for s in to_remove:
            del self.status_effects[s]

    def distance_to(self, target):
        return math.hypot(self.pos[0]-target.pos[0], self.pos[1]-target.pos[1])

    def move_toward(self, target_pos, dt, walls=None, speed_mult=1.0):
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        spd = self.SPEED * speed_mult
        nx = self.pos[0] + dx * spd * dt
        ny = self.pos[1] + dy * spd * dt
        r = pygame.Rect(nx - self.SIZE, ny - self.SIZE, self.SIZE*2, self.SIZE*2)
        blocked = False
        if walls:
            for w in walls:
                if r.colliderect(w):
                    blocked = True
                    break
        if not blocked:
            self.pos[0] = nx
            self.pos[1] = ny
        else:
            perp_x = -dy
            perp_y = dx
            nx2 = self.pos[0] + perp_x * spd * dt
            ny2 = self.pos[1] + perp_y * spd * dt
            r2 = pygame.Rect(nx2 - self.SIZE, ny2 - self.SIZE, self.SIZE*2, self.SIZE*2)
            ok = True
            if walls:
                for w in walls:
                    if r2.colliderect(w):
                        ok = False
                        break
            if ok:
                self.pos[0] = nx2
                self.pos[1] = ny2

    def update(self, dt, player, walls=None, projectile_list=None):
        self.rect = pygame.Rect(self.pos[0]-self.SIZE, self.pos[1]-self.SIZE, self.SIZE*2, self.SIZE*2)
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.update_status(dt)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        self._update_ai(dt, player, walls, projectile_list)

    def _update_ai(self, dt, player, walls, projectile_list):
        self.move_toward(player.pos, dt, walls)
        dist = self.distance_to(player)
        if dist < self.SIZE + 16 and self.attack_cooldown <= 0:
            player.take_damage(self.DAMAGE)
            self.attack_cooldown = self.attack_rate

    def draw(self, surface, camera_offset):
        sx = self.pos[0] - camera_offset[0]
        sy = self.pos[1] - camera_offset[1]
        color = (255, 255, 255) if self.flash_timer > 0 else self.COLOR
        pygame.draw.circle(surface, color, (int(sx), int(sy)), self.SIZE)
        bar_w = self.SIZE * 2
        bar_x = sx - self.SIZE
        bar_y = sy - self.SIZE - 8
        pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, 5))
        fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surface, (200, 50, 50), (bar_x, bar_y, fill, 5))
        if "burn" in self.status_effects:
            pygame.draw.circle(surface, (255, 120, 0), (int(sx), int(sy)), self.SIZE+3, 2)
        if "freeze" in self.status_effects:
            pygame.draw.circle(surface, (100, 200, 255), (int(sx), int(sy)), self.SIZE+3, 2)
        if "poison" in self.status_effects:
            pygame.draw.circle(surface, (100, 255, 100), (int(sx), int(sy)), self.SIZE+3, 2)


# TIER 1
class Crawler(BaseEnemy):
    TIER = 1
    NAME = "Crawler"
    HP = 40
    SPEED = 100
    DAMAGE = 12
    SCORE = 80
    COINS = 2
    COLOR = (180, 80, 60)
    SIZE = 16

    def _update_ai(self, dt, player, walls, proj_list):
        self.move_toward(player.pos, dt, walls)
        dist = self.distance_to(player)
        if dist < self.SIZE + 16 and self.attack_cooldown <= 0:
            player.take_damage(self.DAMAGE)
            self.attack_cooldown = 1.0


class Shooter(BaseEnemy):
    TIER = 1
    NAME = "Shooter"
    HP = 35
    SPEED = 60
    DAMAGE = 8
    SCORE = 100
    COINS = 3
    COLOR = (180, 120, 60)
    SIZE = 16
    PREFERRED_DIST = 200

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        if dist > self.PREFERRED_DIST + 30:
            self.move_toward(player.pos, dt, walls)
        elif dist < self.PREFERRED_DIST - 30:
            dx = self.pos[0] - player.pos[0]
            dy = self.pos[1] - player.pos[1]
            l = math.hypot(dx, dy)
            if l > 0:
                self.move_toward([self.pos[0]+dx/l*50, self.pos[1]+dy/l*50], dt, walls)
        if self.attack_cooldown <= 0 and proj_list is not None and dist < 350:
            dx = player.pos[0] - self.pos[0]
            dy = player.pos[1] - self.pos[1]
            l = math.hypot(dx, dy)
            if l > 0:
                from projectiles import EnemyProjectile
                proj_list.append(EnemyProjectile(self.pos[0], self.pos[1], dx/l, dy/l, 180, self.DAMAGE, (220, 160, 60)))
            self.attack_cooldown = 1.8


class Brute(BaseEnemy):
    TIER = 1
    NAME = "Brute"
    HP = 120
    SPEED = 55
    DAMAGE = 25
    SCORE = 150
    COINS = 5
    COLOR = (160, 60, 60)
    SIZE = 26

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        if self.state == "charge":
            self.state_timer -= dt
            self.move_toward(player.pos, dt, walls, speed_mult=2.2)
            if self.state_timer <= 0:
                self.state = "chase"
                self.state_timer = 2.0
        else:
            self.state_timer -= dt
            self.move_toward(player.pos, dt, walls)
            if self.state_timer <= 0 and dist < 250:
                self.state = "charge"
                self.state_timer = 0.6
        if dist < self.SIZE + 16 and self.attack_cooldown <= 0:
            player.take_damage(self.DAMAGE)
            self.attack_cooldown = 1.2

    def __init__(self, x, y):
        super().__init__(x, y)
        self.state_timer = 2.0


# TIER 2
class SpiderMine(BaseEnemy):
    TIER = 2
    NAME = "SpiderMine"
    HP = 25
    SPEED = 140
    DAMAGE = 35
    SCORE = 120
    COINS = 4
    COLOR = (100, 100, 180)
    SIZE = 14

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        self.move_toward(player.pos, dt, walls)
        if dist < self.SIZE + 16:
            player.take_damage(self.DAMAGE)
            self.hp = 0
            self.alive = False


class Shielder(BaseEnemy):
    TIER = 2
    NAME = "Shielder"
    HP = 80
    SPEED = 65
    DAMAGE = 15
    SCORE = 180
    COINS = 6
    COLOR = (100, 150, 200)
    SIZE = 22

    def __init__(self, x, y):
        super().__init__(x, y)
        self.shield_hp = 60
        self.shield_active = True

    def take_damage(self, amount, source=None):
        if self.shield_active:
            self.shield_hp -= amount
            self.flash_timer = 0.05
            if self.shield_hp <= 0:
                self.shield_active = False
            return
        super().take_damage(amount, source)

    def _update_ai(self, dt, player, walls, proj_list):
        self.move_toward(player.pos, dt, walls)
        dist = self.distance_to(player)
        if dist < self.SIZE + 16 and self.attack_cooldown <= 0:
            player.take_damage(self.DAMAGE)
            self.attack_cooldown = 1.0

    def draw(self, surface, camera_offset):
        super().draw(surface, camera_offset)
        if self.shield_active:
            sx = self.pos[0] - camera_offset[0]
            sy = self.pos[1] - camera_offset[1]
            pygame.draw.circle(surface, (100, 180, 255), (int(sx), int(sy)), self.SIZE + 6, 3)


class Summoner(BaseEnemy):
    TIER = 2
    NAME = "Summoner"
    HP = 60
    SPEED = 45
    DAMAGE = 5
    SCORE = 200
    COINS = 8
    COLOR = (180, 80, 200)
    SIZE = 18

    def __init__(self, x, y):
        super().__init__(x, y)
        self.summon_cooldown = 5.0
        self.summon_timer = 2.0
        self.max_summons = 3
        self.summon_count = 0

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        if dist > 180:
            self.move_toward(player.pos, dt, walls)
        self.summon_timer -= dt
        if self.summon_timer <= 0 and self.summon_count < self.max_summons:
            self.summon_timer = self.summon_cooldown
            from enemies import Crawler
            angle = random.uniform(0, math.pi*2)
            spawn_x = self.pos[0] + math.cos(angle)*60
            spawn_y = self.pos[1] + math.sin(angle)*60
            if proj_list is not None:
                proj_list.append(("summon", Crawler(spawn_x, spawn_y)))
            self.summon_count += 1

    def draw(self, surface, camera_offset):
        super().draw(surface, camera_offset)
        sx = self.pos[0] - camera_offset[0]
        sy = self.pos[1] - camera_offset[1]
        t = pygame.time.get_ticks()/500
        pygame.draw.circle(surface, (220, 100, 255),
                          (int(sx + math.cos(t)*5), int(sy + math.sin(t)*5)), 6)


class Sniper(BaseEnemy):
    TIER = 2
    NAME = "Sniper"
    HP = 45
    SPEED = 50
    DAMAGE = 30
    SCORE = 160
    COINS = 5
    COLOR = (200, 160, 60)
    SIZE = 15

    def __init__(self, x, y):
        super().__init__(x, y)
        self.charge_timer = 0
        self.charging = False
        self.charge_duration = 1.5
        self.target_pos = [0, 0]

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        if dist > 300:
            self.move_toward(player.pos, dt, walls)
        if not self.charging and self.attack_cooldown <= 0 and dist < 500:
            self.charging = True
            self.charge_timer = self.charge_duration
            self.target_pos = list(player.pos)
        if self.charging:
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.charging = False
                self.attack_cooldown = 2.5
                if proj_list is not None:
                    dx = self.target_pos[0] - self.pos[0]
                    dy = self.target_pos[1] - self.pos[1]
                    l = math.hypot(dx, dy)
                    if l > 0:
                        from projectiles import EnemyProjectile
                        proj_list.append(EnemyProjectile(self.pos[0], self.pos[1],
                                                         dx/l, dy/l, 400, self.DAMAGE,
                                                         (255, 220, 0), pierce=True))

    def draw(self, surface, camera_offset):
        super().draw(surface, camera_offset)
        if self.charging:
            sx = self.pos[0] - camera_offset[0]
            sy = self.pos[1] - camera_offset[1]
            tx = self.target_pos[0] - camera_offset[0]
            ty = self.target_pos[1] - camera_offset[1]
            alpha = int(200 * (1 - self.charge_timer/self.charge_duration))
            pygame.draw.line(surface, (255, 220, 0, alpha), (int(sx), int(sy)), (int(tx), int(ty)), 1)


# TIER 3
class TankElite(BaseEnemy):
    TIER = 3
    NAME = "TankElite"
    HP = 300
    SPEED = 50
    DAMAGE = 30
    SCORE = 400
    COINS = 15
    COLOR = (180, 50, 50)
    SIZE = 32

    def __init__(self, x, y):
        super().__init__(x, y)
        self.enrage_threshold = 0.4
        self.enraged = False

    def _update_ai(self, dt, player, walls, proj_list):
        if self.hp / self.max_hp < self.enrage_threshold and not self.enraged:
            self.enraged = True
        spd = 2.0 if self.enraged else 1.0
        self.move_toward(player.pos, dt, walls, speed_mult=spd)
        dist = self.distance_to(player)
        if dist < self.SIZE + 20 and self.attack_cooldown <= 0:
            player.take_damage(self.DAMAGE)
            self.attack_cooldown = 0.8
        if self.attack_cooldown <= 0 and dist < 300 and proj_list is not None:
            if random.random() < 0.02:
                for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    from projectiles import EnemyProjectile
                    proj_list.append(EnemyProjectile(self.pos[0], self.pos[1],
                                                    math.cos(angle), math.sin(angle),
                                                    150, 15, (200, 80, 80)))

    def draw(self, surface, camera_offset):
        super().draw(surface, camera_offset)
        if self.enraged:
            sx = self.pos[0] - camera_offset[0]
            sy = self.pos[1] - camera_offset[1]
            pygame.draw.circle(surface, (255, 50, 0), (int(sx), int(sy)), self.SIZE+4, 3)


class PoisonSpitter(BaseEnemy):
    TIER = 3
    NAME = "PoisonSpitter"
    HP = 80
    SPEED = 70
    DAMAGE = 5
    SCORE = 300
    COINS = 10
    COLOR = (80, 180, 80)
    SIZE = 20

    def _update_ai(self, dt, player, walls, proj_list):
        dist = self.distance_to(player)
        if dist > 200:
            self.move_toward(player.pos, dt, walls)
        if self.attack_cooldown <= 0 and dist < 280 and proj_list is not None:
            for i in range(5):
                angle = math.atan2(player.pos[1]-self.pos[1], player.pos[0]-self.pos[0])
                angle += random.uniform(-0.4, 0.4)
                from projectiles import EnemyProjectile
                proj_list.append(EnemyProjectile(self.pos[0], self.pos[1],
                                                math.cos(angle), math.sin(angle),
                                                160, self.DAMAGE, (80, 220, 80),
                                                poison=True))
            self.attack_cooldown = 2.0


class Teleporter(BaseEnemy):
    TIER = 3
    NAME = "Teleporter"
    HP = 70
    SPEED = 90
    DAMAGE = 20
    SCORE =