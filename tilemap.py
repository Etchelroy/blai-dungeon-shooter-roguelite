import pygame
import random
import math
from settings import *

TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL = 2
TILE_LAVA = 3
TILE_ICE = 4
TILE_SPIKE = 5
TILE_POISON = 6
TILE_CRATE = 7

TILE_COLORS = {
    TILE_FLOOR: [(60, 55, 70), (65, 60, 75), (55, 52, 65)],
    TILE_WALL:  [(40, 35, 50), (45, 40, 55), (35, 32, 45)],
    TILE_LAVA:  [(200, 80, 20), (220, 100, 10), (180, 60, 30)],
    TILE_ICE:   [(160, 200, 230), (170, 210, 240), (150, 190, 220)],
    TILE_SPIKE: [(120, 120, 130), (130, 130, 140), (110, 110, 120)],
    TILE_POISON:[(60, 160, 60), (70, 170, 50), (50, 150, 70)],
    TILE_CRATE: [(160, 120, 60), (170, 130, 70), (150, 110, 50)],
}

HAZARD_TILES = {TILE_LAVA, TILE_SPIKE, TILE_POISON, TILE_ICE}
SOLID_TILES = {TILE_WALL, TILE_EMPTY}
DESTRUCTIBLE_TILES = {TILE_CRATE}

TS = TILE_SIZE  # 16
SCALED = TS * 3  # 48

class Tile:
    def __init__(self, tile_type, variant=0):
        self.type = tile_type
        self.variant = variant
        self.hp = 3 if tile_type == TILE_CRATE else -1
        self.hazard_timer = 0.0
        self.anim_offset = random.random() * math.pi * 2

    def is_solid(self):
        return self.type in SOLID_TILES

    def is_hazard(self):
        return self.type in HAZARD_TILES

    def is_destructible(self):
        return self.type in DESTRUCTIBLE_TILES


def draw_tile_surface(tile_type, variant=0, size=SCALED):
    surf = pygame.Surface((size, size))
    colors = TILE_COLORS.get(tile_type, [(80, 80, 80)])
    base = colors[variant % len(colors)]
    surf.fill(base)

    if tile_type == TILE_FLOOR:
        darker = tuple(max(0, c - 15) for c in base)
        lighter = tuple(min(255, c + 10) for c in base)
        for i in range(0, size, size // 4):
            pygame.draw.line(surf, darker, (i, 0), (i, size), 1)
        for j in range(0, size, size // 4):
            pygame.draw.line(surf, darker, (0, j), (size, j), 1)
        pygame.draw.rect(surf, lighter, (1, 1, size - 2, 2))
        pygame.draw.rect(surf, lighter, (1, 1, 2, size - 2))
        pygame.draw.rect(surf, darker, (0, size - 2, size, 2))
        pygame.draw.rect(surf, darker, (size - 2, 0, 2, size))

    elif tile_type == TILE_WALL:
        darker = tuple(max(0, c - 20) for c in base)
        lighter = tuple(min(255, c + 20) for c in base)
        h = size // 2
        pygame.draw.rect(surf, lighter, (0, 0, size, h - 1))
        pygame.draw.rect(surf, darker, (0, h, size, h))
        pygame.draw.line(surf, (20, 18, 28), (0, h - 1), (size, h - 1), 2)
        pygame.draw.rect(surf, (20, 18, 28), (0, 0, size, size), 1)
        for bx in range(0, size, size // 2):
            pygame.draw.line(surf, (20, 18, 28), (bx + size // 4, 0), (bx + size // 4, h - 1), 1)
        for bx in range(0, size, size // 2):
            pygame.draw.line(surf, (20, 18, 28), (bx, h), (bx, size), 1)

    elif tile_type == TILE_LAVA:
        for i in range(0, size, 6):
            c = (random.randint(180, 220), random.randint(50, 100), 10)
            pygame.draw.circle(surf, c, (random.randint(0, size), random.randint(0, size)), random.randint(2, 6))

    elif tile_type == TILE_ICE:
        pygame.draw.line(surf, (200, 240, 255), (4, 4), (size - 4, size - 4), 2)
        pygame.draw.line(surf, (200, 240, 255), (size - 4, 4), (4, size - 4), 2)

    elif tile_type == TILE_SPIKE:
        pts = [(size // 2, 2), (size - 4, size - 4), (4, size - 4)]
        pygame.draw.polygon(surf, (200, 200, 210), pts)
        pygame.draw.polygon(surf, (80, 80, 90), pts, 2)

    elif tile_type == TILE_POISON:
        pygame.draw.circle(surf, (40, 200, 40), (size // 2, size // 2), size // 3)
        pygame.draw.circle(surf, (20, 150, 20), (size // 2, size // 2), size // 3, 2)

    elif tile_type == TILE_CRATE:
        pygame.draw.rect(surf, (100, 75, 30), (2, 2, size - 4, size - 4), 3)
        pygame.draw.line(surf, (100, 75, 30), (size // 2, 2), (size // 2, size - 2), 2)
        pygame.draw.line(surf, (100, 75, 30), (2, size // 2), (size - 2, size // 2), 2)
        pygame.draw.rect(surf, (20, 15, 5), (0, 0, size, size), 1)

    return surf


class TileCache:
    _cache = {}

    @classmethod
    def get(cls, tile_type, variant=0):
        key = (tile_type, variant)
        if key not in cls._cache:
            cls._cache[key] = draw_tile_surface(tile_type, variant)
        return cls._cache[key]


class TileMap:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.tiles = [[Tile(TILE_EMPTY) for _ in range(cols)] for _ in range(rows)]
        self.hazard_timer = {}

    def get(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[row][col]
        return Tile(TILE_WALL)

    def set(self, col, row, tile_type, variant=None):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            v = variant if variant is not None else random.randint(0, 2)
            self.tiles[row][col] = Tile(tile_type, v)

    def is_solid(self, col, row):
        return self.get(col, row).is_solid()

    def world_to_tile(self, wx, wy):
        return int(wx // SCALED), int(wy // SCALED)

    def tile_to_world(self, col, row):
        return col * SCALED, row * SCALED

    def rect_solid(self, rect):
        left = int(rect.left // SCALED)
        right = int(rect.right // SCALED)
        top = int(rect.top // SCALED)
        bottom = int(rect.bottom // SCALED)
        for r in range(top, bottom + 1):
            for c in range(left, right + 1):
                if self.is_solid(c, r):
                    return True
        return False

    def get_hazard(self, wx, wy):
        col, row = self.world_to_tile(wx, wy)
        t = self.get(col, row)
        if t.is_hazard():
            return t.type
        return None

    def damage_tile(self, col, row, dmg=1):
        t = self.get(col, row)
        if t.is_destructible():
            t.hp -= dmg
            if t.hp <= 0:
                self.set(col, row, TILE_FLOOR, 0)
                return True
        return False

    def update(self, dt):
        pass

    def render(self, screen, camera):
        cam_rect = camera.get_rect()
        c0 = max(0, int(cam_rect.left // SCALED) - 1)
        c1 = min(self.cols, int(cam_rect.right // SCALED) + 2)
        r0 = max(0, int(cam_rect.top // SCALED) - 1)
        r1 = min(self.rows, int(cam_rect.bottom // SCALED) + 2)
        for row in range(r0, r1):
            for col in range(c0, c1):
                tile = self.tiles[row][col]
                if tile.type == TILE_EMPTY:
                    continue
                surf = TileCache.get(tile.type, tile.variant)
                wx = col * SCALED
                wy = row * SCALED
                sx, sy = camera.world_to_screen(wx, wy)
                screen.blit(surf, (sx, sy))