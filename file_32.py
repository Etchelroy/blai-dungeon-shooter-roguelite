import pygame
from settings import TILE_PX, COLS, ROWS, ARENA_W, ARENA_H
from assets import make_floor_tile, make_wall_tile, make_lava_tile, make_ice_tile, make_spike_tile, make_poison_tile

TILE_FLOOR = 0
TILE_WALL = 1
TILE_LAVA = 2
TILE_ICE = 3
TILE_SPIKE = 4
TILE_POISON = 5

HAZARD_TILES = {TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON}

class Tilemap:
    def __init__(self):
        self.cols = COLS
        self.rows = ROWS
        self.tiles = [[TILE_FLOOR]*self.cols for _ in range(self.rows)]
        self.variants = [[0]*self.cols for _ in range(self.rows)]
        self._lava_t = 0.0
        self._lava_surf = None

    def set(self, col, row, tile_type, variant=0):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.tiles[row][col] = tile_type
            self.variants[row][col] = variant

    def get(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[row][col]
        return TILE_WALL

    def world_to_tile(self, wx, wy):
        return int(wx // TILE_PX), int(wy // TILE_PX)

    def tile_rect(self, col, row):
        return pygame.Rect(col*TILE_PX, row*TILE_PX, TILE_PX, TILE_PX)

    def is_solid(self, col, row):
        return self.get(col, row) == TILE_WALL

    def is_solid_world(self, wx, wy):
        return self.is_solid(*self.world_to_tile(wx, wy))

    def update(self, dt):
        self._lava_t += dt

    def get_tile_surf(self, tile, variant):
        if tile == TILE_FLOOR:
            return make_floor_tile(variant)
        elif tile == TILE_WALL:
            return make_wall_tile(variant)
        elif tile == TILE_LAVA:
            return make_lava_tile(self._lava_t)
        elif tile == TILE_ICE:
            return make_ice_tile()
        elif tile == TILE_SPIKE:
            return make_spike_tile()
        elif tile == TILE_POISON:
            return make_poison_tile()
        return make_floor_tile(0)

    def draw(self, surface, cam_ox, cam_oy):
        from settings import SCREEN_W, SCREEN_H
        col0 = max(0, int(cam_ox // TILE_PX))
        row0 = max(0, int(cam_oy // TILE_PX))
        col1 = min(self.cols, col0 + SCREEN_W // TILE_PX + 2)
        row1 = min(self.rows, row0 + SCREEN_H // TILE_PX + 2)
        for row in range(row0, row1):
            for col in range(col0, col1):
                t = self.tiles[row][col]
                v = self.variants[row][col]
                surf = self.get_tile_surf(t, v)
                sx = col*TILE_PX - int(cam_ox)
                sy = row*TILE_PX - int(cam_oy)
                surface.blit(surf, (sx, sy))