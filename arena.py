import pygame
import random
import math

TILE_SIZE = 64
FLOOR = 0
WALL = 1
LAVA = 2
ICE = 3
SPIKES = 4
POISON = 5

TILE_COLORS = {
    FLOOR: [(60, 60, 70), (55, 55, 65), (65, 65, 75)],
    WALL: [(40, 40, 50), (35, 35, 45), (45, 40, 55)],
    LAVA: [(200, 80, 0), (220, 100, 0), (180, 60, 0)],
    ICE: [(150, 200, 230), (160, 210, 240), (140, 190, 220)],
    SPIKES: [(80, 80, 90), (70, 70, 80), (90, 90, 100)],
    POISON: [(50, 120, 50), (40, 110, 40), (60, 130, 60)],
}

class Crate:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.hp = 30
        self.max_hp = 30
        self.alive = True
        self.rect = pygame.Rect(x - 24, y - 24, 48, 48)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.pos[0], self.pos[1])
        r = pygame.Rect(int(sx)-24, int(sy)-24, 48, 48)
        ratio = self.hp / self.max_hp
        shade = int(100 + 55 * ratio)
        pygame.draw.rect(surface, (shade, int(shade*0.6), 30), r)
        pygame.draw.rect(surface, (200, 150, 80), r, 2)
        # X pattern
        pygame.draw.line(surface, (150, 100, 50), (int(sx)-20, int(sy)-20), (int(sx)+20, int(sy)+20), 2)
        pygame.draw.line(surface, (150, 100, 50), (int(sx)+20, int(sy)-20), (int(sx)-20, int(sy)+20), 2)


class Hazard:
    def __init__(self, x, y, htype, tile_x, tile_y):
        self.pos = [x, y]
        self.type = htype
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.timer = 0
        self.damage_timer = 0
        self.anim = random.uniform(0, math.pi * 2)

    def update(self, dt, player, particles):
        self.timer += dt
        self.anim += dt * 2
        self.damage_timer -= dt

        px, py = player.pos
        dist = math.hypot(px - self.pos[0], py - self.pos[1])
        if dist < TILE_SIZE * 0.6 and self.damage_timer <= 0:
            if self.type == LAVA:
                player.take_damage(5)
                self.damage_timer = 0.5
                _spawn_hazard_particles(particles, self.pos, (255, 100, 0))
            elif self.type == SPIKES:
                player.take_damage(15)
                self.damage_timer = 1.0
                _spawn_hazard_particles(particles, self.pos, (200, 200, 200))
            elif self.type == POISON:
                player.apply_poison(3, 3.0)
                self.damage_timer = 1.5
                _spawn_hazard_particles(particles, self.pos, (50, 200, 50))
            elif self.type == ICE:
                player.apply_slow(0.5, 2.0)
                self.damage_timer = 0.5

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.pos[0], self.pos[1])
        if self.type == LAVA:
            pulse = abs(math.sin(self.anim)) * 30
            color = (200 + int(pulse), 60, 0)
            pygame.draw.rect(surface, color,
                           (int(sx)-32, int(sy)-32, 64, 64))
            for i in range(3):
                bx = sx + math.sin(self.anim + i*2) * 10
                by = sy - 10 + math.cos(self.anim + i) * 5
                pygame.draw.circle(surface, (255, 180, 0), (int(bx), int(by)), 4)
        elif self.type == ICE:
            color = (150, 200, 230)
            pygame.draw.rect(surface, color, (int(sx)-32, int(sy)-32, 64, 64))
            pygame.draw.line(surface, (200, 230, 255),
                           (int(sx)-20, int(sy)), (int(sx)+20, int(sy)), 2)
            pygame.draw.line(surface, (200, 230, 255),
                           (int(sx), int(sy)-20), (int(sx), int(sy)+20), 2)
        elif self.type == SPIKES:
            pygame.draw.rect(surface, (70, 70, 80), (int(sx)-32, int(sy)-32, 64, 64))
            for i in range(4):
                bx = sx - 24 + i * 16
                pts = [(int(bx), int(sy)+16), (int(bx)+8, int(sy)-16),
                       (int(bx)+16, int(sy)+16)]
                pygame.draw.polygon(surface, (180, 180, 190), pts)
        elif self.type == POISON:
            pulse = abs(math.sin(self.anim)) * 20
            color = (30 + int(pulse), 100, 30)
            pygame.draw.rect(surface, color, (int(sx)-32, int(sy)-32, 64, 64))
            for i in range(3):
                bx = sx + math.cos(self.anim*0.7 + i*2.1) * 12
                by = sy + math.sin(self.anim*0.7 + i*2.1) * 12
                pygame.draw.circle(surface, (80, 220, 80), (int(bx), int(by)), 5)


def _spawn_hazard_particles(particles, pos, color):
    from particles import Particle
    for _ in range(3):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(20, 60)
        p = Particle(pos[0], pos[1],
                    math.cos(angle)*speed, math.sin(angle)*speed,
                    color, random.uniform(0.2, 0.5), 4)
        particles.append(p)


class Arena:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.tiles = [[FLOOR]*height for _ in range(width)]
        self.tile_variants = [[0]*height for _ in range(width)]
        self.hazards = []
        self.crates = []
        self.spawn_points = []
        self.player_spawn = (width * TILE_SIZE // 2, height * TILE_SIZE // 2)
        self._generate()

    def _generate(self):
        w, h = self.width, self.height
        # Border walls
        for x in range(w):
            for y in range(h):
                self.tile_variants[x][y] = random.randint(0, 2)
                if x == 0 or x == w-1 or y == 0 or y == h-1:
                    self.tiles[x][y] = WALL
                else:
                    self.tiles[x][y] = FLOOR

        # Random wall clusters
        for _ in range(20):
            cx = random.randint(3, w-4)
            cy = random.randint(3, h-4)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if random.random() < 0.6:
                        nx, ny = cx+dx, cy+dy
                        # Keep center clear
                        if abs(nx - w//2) > 4 or abs(ny - h//2) > 4:
                            self.tiles[nx][ny] = WALL

        # Hazard zones
        hazard_types = [LAVA, ICE, SPIKES, POISON]
        for _ in range(8):
            htype = random.choice(hazard_types)
            hx = random.randint(3, w-4)
            hy = random.randint(3, h-4)
            if abs(hx - w//2) < 5 and abs(hy - h//2) < 5:
                continue
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = hx+dx, hy+dy
                    if 1 <= nx < w-1 and 1 <= ny < h-1:
                        if self.tiles[nx][ny] == FLOOR:
                            self.tiles[nx][ny] = htype
                            wx = nx * TILE_SIZE + TILE_SIZE // 2
                            wy = ny * TILE_SIZE + TILE_SIZE // 2
                            self.hazards.append(Hazard(wx, wy, htype, nx, ny))

        # Crates
        for _ in range(15):
            cx = random.randint(3, w-4)
            cy = random.randint(3, h-4)
            if self.tiles[cx][cy] == FLOOR:
                if abs(cx - w//2) > 3 or abs(cy - h//2) > 3:
                    wx = cx * TILE_SIZE + TILE_SIZE // 2
                    wy = cy * TILE_SIZE + TILE_SIZE // 2
                    self.crates.append(Crate(wx, wy))

        # Spawn points for enemies
        for _ in range(30):
            sx = random.randint(2, w-3)
            sy = random.randint(2, h-3)
            if self.tiles[sx][sy] == FLOOR:
                dist = math.hypot(sx - w//2, sy - h//2)
                if dist > 5:
                    self.spawn_points.append((sx * TILE_SIZE + TILE_SIZE//2,
                                              sy * TILE_SIZE + TILE_SIZE//2))

    def get_wall_rects(self):
        rects = []
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == WALL:
                    rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return rects

    def is_wall(self, wx, wy):
        tx = int(wx // TILE_SIZE)
        ty = int(wy // TILE_SIZE)
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.tiles[tx][ty] == WALL
        return True

    def update(self, dt, player, particles):
        for h in self.hazards:
            h.update(dt, player, particles)
        for c in self.crates[:]:
            if not c.alive:
                from particles import Particle
                for _ in range(8):
                    angle = random.uniform(0, math.pi * 2)
                    p = Particle(c.pos[0], c.pos[1],
                                math.cos(angle)*80, math.sin(angle)*80,
                                (150, 100, 50), random.uniform(0.3, 0.8), 5)
                    particles.append(p)
                self.crates.remove(c)

    def draw(self, surface, camera):
        screen_w, screen_h = surface.get_size()
        # Determine visible tile range
        cam_x, cam_y = camera.offset_x, camera.offset_y
        start_tx = max(0, int(cam_x // TILE_SIZE) - 1)
        start_ty = max(0, int(cam_y // TILE_SIZE) - 1)
        end_tx = min(self.width, start_tx + screen_w // TILE_SIZE + 3)
        end_ty = min(self.height, start_ty + screen_h // TILE_SIZE + 3)

        for x in range(start_tx, end_tx):
            for y in range(start_ty, end_ty):
                ttype = self.tiles[x][y]
                if ttype in (LAVA, ICE, SPIKES, POISON):
                    # Drawn by hazard objects
                    # Draw floor under
                    sx = x * TILE_SIZE - cam_x
                    sy = y * TILE_SIZE - cam_y
                    colors = TILE_COLORS[FLOOR]
                    variant = self.tile_variants[x][y]
                    pygame.draw.rect(surface, colors[variant % len(colors)],
                                   (int(sx), int(sy), TILE_SIZE, TILE_SIZE))
                    continue
                colors = TILE_COLORS.get(ttype, TILE_COLORS[FLOOR])
                variant = self.tile_variants[x][y]
                color = colors[variant % len(colors)]
                sx = x * TILE_SIZE - cam_x
                sy = y * TILE_SIZE - cam_y
                pygame.draw.rect(surface, color, (int(sx), int(sy), TILE_SIZE, TILE_SIZE))
                if ttype == WALL:
                    highlight = tuple(min(255, c+20) for c in color)
                    pygame.draw.rect(surface, highlight,
                                   (int(sx), int(sy), TILE_SIZE, 3))
                    pygame.draw.rect(surface, highlight,
                                   (int(sx), int(sy), 3, TILE_SIZE))
                elif ttype == FLOOR:
                    # Grid lines
                    pygame.draw.rect(surface, tuple(max(0,c-10) for c in color),
                                   (int(sx), int(sy), TILE_SIZE, TILE_SIZE), 1)

        # Draw hazard overlays
        for h in self.hazards:
            hsx, hsy = camera.world_to_screen(h.pos[0], h.pos[1])
            if -64 < hsx < screen_w+64 and -64 < hsy < screen_h+64:
                h.draw(surface, camera)

        # Draw crates
        for c in self.crates:
            csx, csy = camera.world_to_screen(c.pos[0], c.pos[1])
            if -64 < csx < screen_w+64 and -64 < csy < screen_h+64:
                c.draw(surface, camera)