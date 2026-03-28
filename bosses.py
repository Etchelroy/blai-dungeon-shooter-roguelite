import pygame
import math
import random
from constants import *

class BossBase:
    def __init__(self, x, y, name, hp, color, size=48):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.size = size
        self.alive = True
        self.phase = 1
        self.phase_transitions = [0.66, 0.33]
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 60
        self.damage_flash = 0.0
        self.attack_timer = 0.0
        self.stun_timer = 0.0
        self.drop_coins = 20
        self.score_value = 5000
        self.death_sequence = False
        self.death_timer = 3.0
        self.vulnerable = True
        self.vulnerability_timer = 0.0
        self.invuln_timer = 0.0
        self.image = self._make_image()
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.angle = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surf, (255,255,255), (self.size, self.size), self.size, 3)
        return surf

    def get_rect(self):
        return pygame.Rect(int(self.x-self.size), int(self.y-self.size), self.size*2, self.size*2)

    def take_damage(self, amount, kx=0, ky=0):
        if not self.vulnerable or self.invuln_timer > 0:
            return
        self.hp -= amount
        self.damage_flash = 0.2
        self.knockback_x = kx * 100
        self.knockback_y = ky * 100
        if self.hp <= 0:
            self.hp = 0
            if not self.death_sequence:
                self.death_sequence = True
        else:
            hp_ratio = self.hp / self.max_hp
            if self.phase == 1 and hp_ratio <= self.phase_transitions[0]:
                self.phase = 2
                self.on_phase_change(2)
            elif self.phase == 2 and hp_ratio <= self.phase_transitions[1]:
                self.phase = 3
                self.on_phase_change(3)

    def on_phase_change(self, phase):
        self.invuln_timer = 2.0
        self.speed += 20

    def update(self, dt, player, walls, projectiles_out, particles_out):
        if self.death_sequence:
            self.death_timer -= dt
            self._death_effect(dt, particles_out)
            return self.death_timer <= 0

        if self.stun_timer > 0:
            self.stun_timer -= dt
        if self.damage_flash > 0:
            self.damage_flash -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            self.vulnerable = False
        else:
            self.vulnerable = True
        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.knockback_x *= (1 - 5*dt)
        self.knockback_y *= (1 - 5*dt)
        self.x += self.knockback_x * dt
        self.y += self.knockback_y * dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx,dy)
        if dist > 0:
            self.angle = math.atan2(dy,dx)

        self.phase_update(dt, player, walls, projectiles_out, particles_out)
        return False

    def phase_update(self, dt, player, walls, projectiles_out, particles_out):
        pass

    def _death_effect(self, dt, particles_out):
        if random.random() < 0.3:
            from particles import Particle
            px = self.x + random.uniform(-self.size, self.size)
            py = self.y + random.uniform(-self.size, self.size)
            particles_out.append(Particle(px, py,
                random.uniform(-100,100), random.uniform(-100,100),
                random.choice([(255,100,0),(255,200,50),(220,80,0)]),
                random.uniform(0.3,0.8), random.uniform(3,8)))

    def _move_toward(self, tx, ty, dt, walls):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            nx, ny = dx/dist, dy/dist
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt

    def _shoot_radial(self, count, speed, damage, color, projectiles_out):
        from projectiles import EnemyProjectile
        for i in range(count):
            a = i * math.pi * 2 / count
            projectiles_out.append(EnemyProjectile(self.x, self.y, math.cos(a), math.sin(a),
                speed=speed, damage=damage, color=color))

    def _shoot_at_player(self, player, speed, damage, color, projectiles_out, spread=0):
        from projectiles import EnemyProjectile
        dx = player.x - self.x
        dy = player.y - self.y
        d = math.hypot(dx,dy)
        if d == 0: return
        base_a = math.atan2(dy,dx)
        a = base_a + random.uniform(-spread, spread)
        projectiles_out.append(EnemyProjectile(self.x, self.y, math.cos(a), math.sin(a),
            speed=speed, damage=damage, color=color))

    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x)
        sy = int(self.y - camera.offset_y)
        if self.damage_flash > 0 and int(self.damage_flash*20)%2==0:
            img = self.image.copy()
            img.fill((255,80,80,0), special_flags=pygame.BLEND_ADD)
            surface.blit(img, (sx-self.size, sy-self.size))
        else:
            surface.blit(self.image, (sx-self.size, sy-self.size))
        if not self.vulnerable:
            pygame.draw.circle(surface, (200,200,200,100), (sx,sy), self.size+6, 3)

class BossVoidBringer(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Void Bringer", hp=1500, color=(80,0,120), size=48)
        self.orbit_angle = 0.0
        self.orbit_speed = 1.5
        self.wave_timer = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80,0,120), (self.size,self.size), self.size)
        for i in range(6):
            a = i * math.pi/3
            x1 = self.size + math.cos(a)*20
            y1 = self.size + math.sin(a)*20
            x2 = self.size + math.cos(a)*self.size
            y2 = self.size + math.sin(a)*self.size
            pygame.draw.line(surf, (200,100,255), (int(x1),int(y1)), (int(x2),int(y2)), 3)
        pygame.draw.circle(surf, (200,100,255), (self.size,self.size), 15)
        pygame.draw.circle(surf, (255,255,255), (self.size,self.size), self.size, 2)
        return surf

    def on_phase_change(self, phase):
        super().on_phase_change(phase)
        self.orbit_speed += 0.8

    def phase_update(self, dt, player, walls, projectiles_out, particles_out):
        self.orbit_angle += self.orbit_speed * dt
        if self.phase == 1:
            self._phase1(dt, player, walls, projectiles_out)
        elif self.phase == 2:
            self._phase2(dt, player, walls, projectiles_out)
        else:
            self._phase3(dt, player, walls, projectiles_out, particles_out)

    def _phase1(self, dt, player, walls, projectiles_out):
        self._move_toward(player.x, player.y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 2.0
            self._shoot_radial(8, 180, 12, (180,80,255), projectiles_out)

    def _phase2(self, dt, player, walls, projectiles_out):
        # Orbit player
        target_x = player.x + math.cos(self.orbit_angle) * 200
        target_y = player.y + math.sin(self.orbit_angle) * 200
        self._move_toward(target_x, target_y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 1.5
            self._shoot_radial(12, 200, 15, (220,80,255), projectiles_out)
            self._shoot_at_player(player, 300, 18, (255,200,255), projectiles_out)

    def _phase3(self, dt, player, walls, projectiles_out, particles_out):
        self.wave_timer -= dt
        target_x = player.x + math.cos(self.orbit_angle) * 150
        target_y = player.y + math.sin(self.orbit_angle) * 150
        self._move_toward(target_x, target_y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 1.0
            self._shoot_radial(16, 220, 18, (255,100,255), projectiles_out)
        if self.wave_timer <= 0:
            self.wave_timer = 3.0
            for i in range(24):
                a = i * math.pi*2/24
                self._shoot_at_player(player, 250+random.uniform(-50,50), 20,
                                     (200,50,255), projectiles_out, spread=0.1)

class BossInferno(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Inferno", hp=1800, color=(220,80,20), size=52)
        self.flame_wall_timer = 0.0
        self.dash_timer = 0.0
        self.dashing = False
        self.dash_vx = 0
        self.dash_vy = 0
        self.dash_dur = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (220,80,20), (0,0,self.size*2, self.size*2))
        pygame.draw.ellipse(surf, (255,160,50), (8,8, self.size*2-16, self.size*2-16))
        pygame.draw.ellipse(surf, (255,220,100), (self.size-10, self.size-10, 20,20))
        for i in range(8):
            a = i * math.pi/4
            x1 = self.size + math.cos(a)*(self.size-8)
            y1 = self.size + math.sin(a)*(self.size-8)
            x2 = self.size + math.cos(a)*self.size + random.uniform(-4,4)
            y2 = self.size + math.sin(a)*self.size + random.uniform(-4
I'll implement the remaining files needed to complete the game.

```python
# filename: arena.py
import pygame
import random
import math
from constants import *

TILE_FLOOR = 0
TILE_WALL = 1
TILE_LAVA = 2
TILE_ICE = 3
TILE_SPIKES = 4
TILE_POISON = 5

TILE_SIZE = 64

class Crate:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.hp = 30
        self.alive = True
        self.color = (139, 90, 43)
        self.drop_chance = 0.3

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        r = pygame.Rect(sx, sy, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, (100, 60, 20), r, 3)
        # cross lines
        pygame.draw.line(surface, (100, 60, 20), (sx+4, sy+4), (sx+44, sy+44), 2)
        pygame.draw.line(surface, (100, 60, 20), (sx+44, sy+4), (sx+4, sy+44), 2)

class Hazard:
    def __init__(self, x, y, htype):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.htype = htype
        self.timer = 0
        self.pulse = 0

    def update(self, dt):
        self.timer += dt
        self.pulse = math.sin(self.timer * 3) * 0.5 + 0.5

    def get_effect(self):
        if self.htype == TILE_LAVA:
            return {'damage': 15, 'type': 'fire'}
        elif self.htype == TILE_ICE:
            return {'damage': 0, 'type': 'slow', 'factor': 0.5}
        elif self.htype == TILE_SPIKES:
            return {'damage': 20, 'type': 'pierce'}
        elif self.htype == TILE_POISON:
            return {'damage': 5, 'type': 'poison', 'duration': 3.0}
        return {}

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        r = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)
        if self.htype == TILE_LAVA:
            c = (int(200 + 55 * self.pulse), int(60 * self.pulse), 0)
            pygame.draw.rect(surface, c, r)
            for i in range(3):
                bx = sx + random.randint(0, TILE_SIZE)
                by = sy + random.randint(0, TILE_SIZE)
                pygame.draw.circle(surface, (255, 150, 0), (bx, by), 3)
        elif self.htype == TILE_ICE:
            c = (int(100 + 80 * self.pulse), int(180 + 60 * self.pulse), 255)
            pygame.draw.rect(surface, c, r)
            pygame.draw.line(surface, (200, 240, 255), (sx+8, sy+32), (sx+56, sy+32), 2)
            pygame.draw.line(surface, (200, 240, 255), (sx+32, sy+8), (sx+32, sy+56), 2)
        elif self.htype == TILE_SPIKES:
            pygame.draw.rect(surface, (80, 80, 80), r)
            for i in range(4):
                tx = sx + 8 + i * 14
                pts = [(tx, sy+TILE_SIZE), (tx+7, sy+8), (tx+14, sy+TILE_SIZE)]
                pygame.draw.polygon(surface, (160, 160, 180), pts)
        elif self.htype == TILE_POISON:
            c = (int(40 + 30 * self.pulse), int(120 + 40 * self.pulse), 20)
            pygame.draw.rect(surface, c, r)
            for i in range(2):
                bx = sx + random.randint(8, 56)
                by = sy + random.randint(8, 56)
                pygame.draw.circle(surface, (80, 200, 40), (bx, by), 4)

class Arena:
    def __init__(self, width=25, height=25):
        self.width = width
        self.height = height
        self.tiles = []
        self.walls = []
        self.hazards = []
        self.crates = []
        self.floor_rects = []
        self.spawn_points = []
        self.player_spawn = (width * TILE_SIZE // 2, height * TILE_SIZE // 2)
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        self._generate()

    def _generate(self):
        w, h = self.width, self.height
        grid = [[TILE_WALL] * w for _ in range(h)]

        # Cellular automata
        for y in range(1, h-1):
            for x in range(1, w-1):
                grid[y][x] = TILE_FLOOR if random.random() > 0.4 else TILE_WALL

        for _ in range(4):
            new = [row[:] for row in grid]
            for y in range(1, h-1):
                for x in range(1, w-1):
                    walls = sum(1 for dy in [-1,0,1] for dx in [-1,0,1]
                                if grid[y+dy][x+dx] == TILE_WALL)
                    new[y][x] = TILE_WALL if walls >= 5 else TILE_FLOOR
            grid = new

        # Force center open
        cx, cy = w//2, h//2
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 < cy+dy < h-1 and 0 < cx+dx < w-1:
                    grid[cy+dy][cx+dx] = TILE_FLOOR

        self.tiles = grid
        self.walls = []
        self.floor_rects = []

        floor_cells = []
        for y in range(h):
            for x in range(w):
                rx = x * TILE_SIZE
                ry = y * TILE_SIZE
                r = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
                if grid[y][x] == TILE_WALL:
                    self.walls.append(r)
                else:
                    self.floor_rects.append(r)
                    floor_cells.append((x, y))

        # Hazards
        htype_list = [TILE_LAVA, TILE_ICE, TILE_SPIKES, TILE_POISON]
        hazard_count = max(4, len(floor_cells) // 20)
        used = set()
        for _ in range(hazard_count):
            attempts = 0
            while attempts < 20:
                cell = random.choice(floor_cells)
                x, y = cell
                dist = math.hypot(x - cx, y - cy)
                if dist > 4 and cell not in used:
                    used.add(cell)
                    htype = random.choice(htype_list)
                    self.hazards.append(Hazard(x*TILE_SIZE, y*TILE_SIZE, htype))
                    break
                attempts += 1

        # Crates
        crate_count = max(3, len(floor_cells) // 25)
        for _ in range(crate_count):
            attempts = 0
            while attempts < 20:
                cell = random.choice(floor_cells)
                x, y = cell
                dist = math.hypot(x - cx, y - cy)
                cx2 = x * TILE_SIZE + 8
                cy2 = y * TILE_SIZE + 8
                if dist > 3 and cell not in used:
                    used.add(cell)
                    self.crates.append(Crate(cx2, cy2))
                    break
                attempts += 1

        # Spawn points (edges of open area)
        self.spawn_points = []
        for cell in floor_cells:
            x, y = cell
            dist = math.hypot(x - cx, y - cy)
            if dist > 6:
                self.spawn_points.append((x * TILE_SIZE + TILE_SIZE//2,
                                          y * TILE_SIZE + TILE_SIZE//2))

        self.player_spawn = (cx * TILE_SIZE + TILE_SIZE//2,
                             cy * TILE_SIZE + TILE_SIZE//2)

    def get_wall_rects(self):
        return self.walls

    def get_crate_rects(self):
        return [c.rect for c in self.crates if c.alive]

    def get_solid_rects(self):
        return self.walls + self.get_crate_rects()

    def update(self, dt):
        for h in self.hazards:
            h.update(dt)
        self.crates = [c for c in self.crates if c.alive]

    def check_hazards(self, rect):
        effects = []
        for h in self.hazards:
            if h.rect.colliderect(rect):
                effects.append(h.get_effect())
        return effects

    def get_random_spawn(self):
        if self.spawn_points:
            return random.choice(self.spawn_points)
        return self.player_spawn

    def draw_floor(self, surface, camera):
        colors = [(50, 45, 42), (48, 43, 40), (52, 47, 44)]
        for r in self.floor_rects:
            sx, sy = camera.world_to_screen(r.x, r.y)
            if -TILE_SIZE <= sx <= SCREEN_W and -TILE_SIZE <= sy <= SCREEN_H:
                c = colors[(r.x // TILE_SIZE + r.y // TILE_SIZE) % 3]
                pygame.draw.rect(surface, c, pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE))

    def draw_walls(self, surface, camera):
        for r in self.walls:
            sx, sy = camera.world_to_screen(r.x, r.y)
            if -TILE_SIZE <= sx <= SCREEN_W and -TILE_SIZE <= sy <= SCREEN_H:
                pygame.draw.rect(surface, (30, 28, 26), pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(surface, (20, 18, 16), pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE), 2)

    def draw_hazards(self, surface, camera):
        for h in self.hazards:
            sx, sy = camera.world_to_screen(h.rect.x, h.rect.y)
            if -TILE_SIZE <= sx <= SCREEN_W and -TILE_SIZE <= sy <= SCREEN_H:
                h.draw(surface, camera)

    def draw_crates(self, surface, camera):
        for c in self.crates:
            c.draw(surface, camera)

    def draw(self, surface, camera):
        self.draw_floor(surface, camera)
        self.draw_hazards(surface, camera)
        self.draw_walls(surface, camera)
        self.draw_crates(surface, camera)