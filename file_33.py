import random
import math
import pygame
from settings import COLS, ROWS, TILE_PX, ARENA_W, ARENA_H
from tilemap import Tilemap, TILE_FLOOR, TILE_WALL, TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON
from assets import make_crate_sprite

class Crate:
    def __init__(self, x, y, hp=30):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.rect = pygame.Rect(x, y, TILE_PX-4, TILE_PX-4)
        self.alive = True

    def take_damage(self, dmg, particles=None):
        self.hp -= dmg
        if particles:
            particles.burst(self.rect.centerx, self.rect.centery, 6, (160,110,60), speed=80, life=0.4)
        if self.hp <= 0:
            self.alive = False
            if particles:
                particles.burst(self.rect.centerx, self.rect.centery, 16, (160,110,60), speed=120, life=0.6)

    def draw(self, surface, cam_ox, cam_oy):
        sx = self.rect.x - int(cam_ox)
        sy = self.rect.y - int(cam_oy)
        surf = make_crate_sprite(self.hp/self.max_hp)
        surface.blit(surf, (sx, sy))

class Arena:
    def __init__(self):
        self.tilemap = Tilemap()
        self.crates = []
        self.spawn_points = []
        self.player_start = (ARENA_W//2, ARENA_H//2)
        self._hazard_rects = []
        self.generate()

    def generate(self, seed=None):
        rng = random.Random(seed)
        tm = self.tilemap
        # Fill borders with walls
        for row in range(ROWS):
            for col in range(COLS):
                if row == 0 or row == ROWS-1 or col == 0 or col == COLS-1:
                    tm.set(col, row, TILE_WALL, rng.randint(0,2))
                else:
                    tm.set(col, row, TILE_FLOOR, rng.randint(0,2))

        # Random wall clusters
        for _ in range(18):
            cx = rng.randint(3, COLS-4)
            cy = rng.randint(3, ROWS-4)
            w = rng.randint(1, 4)
            h = rng.randint(1, 4)
            for r in range(cy, min(cy+h, ROWS-1)):
                for c in range(cx, min(cx+w, COLS-1)):
                    # Keep center clear
                    if abs(c - COLS//2) > 3 or abs(r - ROWS//2) > 3:
                        tm.set(c, r, TILE_WALL, rng.randint(0,2))

        # Hazard zones
        hazard_types = [TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON]
        self._hazard_rects.clear()
        for _ in range(6):
            htype = rng.choice(hazard_types)
            hx = rng.randint(3, COLS-8)
            hy = rng.randint(3, ROWS-8)
            hw = rng.randint(2, 5)
            hh = rng.randint(2, 4)
            for r in range(hy, min(hy+hh, ROWS-1)):
                for c in range(hx, min(hx+hw, COLS-1)):
                    if abs(c - COLS//2) > 4 or abs(r - ROWS//2) > 4:
                        tm.set(c, r, htype)
                        rect = pygame.Rect(c*TILE_PX, r*TILE_PX, TILE_PX, TILE_PX)
                        self._hazard_rects.append((rect, htype))

        # Crates
        self.crates.clear()
        for _ in range(20):
            cx = rng.randint(2, COLS-3) * TILE_PX + 2
            cy = rng.randint(2, ROWS-3) * TILE_PX + 2
            tc, tr = self.tilemap.world_to_tile(cx, cy)
            if not self.tilemap.is_solid(tc, tr):
                self.crates.append(Crate(cx, cy, rng.randint(20,40)))

        # Spawn points (edges of center area)
        self.spawn_points.clear()
        for i in range(20):
            a = i * 2 * math.pi / 20
            r = rng.uniform(180, 400)
            sx = ARENA_W//2 + math.cos(a)*r
            sy = ARENA_H//2 + math.sin(a)*r
            sx = max(TILE_PX*2, min(ARENA_W-TILE_PX*2, sx))
            sy = max(TILE_PX*2, min(ARENA_H-TILE_PX*2, sy))
            self.spawn_points.append((sx, sy))

        self.player_start = (ARENA_W//2, ARENA_H//2)

    def get_hazard_at(self, wx, wy):
        from tilemap import TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON
        col, row = self.tilemap.world_to_tile(wx, wy)
        t = self.tilemap.get(col, row)
        if t in (TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON):
            return t
        return None

    def update(self, dt, particles=None):
        self.tilemap.update(dt)
        self.crates = [c for c in self.crates if c.alive]

    def draw(self, surface, cam_ox, cam_oy):
        self.tilemap.draw(surface, cam_ox, cam_oy)
        for c in self.crates:
            c.draw(surface, cam_ox, cam_oy)

    def get_wall_rects(self):
        rects = []
        tm = self.tilemap
        for row in range(ROWS):
            for col in range(COLS):
                if tm.is_solid(col, row):
                    rects.append(pygame.Rect(col*TILE_PX, row*TILE_PX, TILE_PX, TILE_PX))
        return rects

    def get_solid_rects_near(self, wx, wy, radius=200):
        rects = []
        tm = self.tilemap
        col0 = max(0, int((wx-radius)//TILE_PX))
        col1 = min(COLS, int((wx+radius)//TILE_PX)+1)
        row0 = max(0, int((wy-radius)//TILE_PX))
        row1 = min(ROWS, int((wy+radius)//TILE_PX)+1)
        for row in range(row0, row1):
            for col in range(col0, col1):
                if tm.is_solid(col, row):
                    rects.append(pygame.Rect(col*TILE_PX, row*TILE_PX, TILE_PX, TILE_PX))
        for c in self.crates:
            rects.append(c.rect)
        return rects