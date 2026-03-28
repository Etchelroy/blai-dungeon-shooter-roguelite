import pygame
import random
import math
from settings import *
from tilemap import TileMap, Tile, TILE_FLOOR, TILE_WALL, TILE_LAVA, TILE_ICE, TILE_SPIKE, TILE_POISON, TILE_CRATE, SCALED

ARENA_COLS = ARENA_W // (TILE_SIZE * 3)
ARENA_ROWS = ARENA_H // (TILE_SIZE * 3)

class Room:
    def __init__(self, col, row, w, h):
        self.col = col
        self.row = row
        self.w = w
        self.h = h

    def center(self):
        return self.col + self.w // 2, self.row + self.h // 2

    def intersects(self, other, margin=1):
        return (self.col - margin < other.col + other.w + margin and
                self.col + self.w + margin > other.col - margin and
                self.row - margin < other.row + other.h + margin and
                self.row + self.h + margin > other.row - margin)


class Arena:
    def __init__(self):
        self.tilemap = TileMap(ARENA_COLS, ARENA_ROWS)
        self.rooms = []
        self.spawn_points = []
        self.player_start = (ARENA_W // 2, ARENA_H // 2)
        self.hazard_lights = []

    def generate(self, wave=1):
        self.rooms.clear()
        self.spawn_points.clear()
        self.hazard_lights.clear()
        tm = self.tilemap
        # Fill with walls
        for row in range(ARENA_ROWS):
            for col in range(ARENA_COLS):
                tm.set(col, row, TILE_WALL, random.randint(0, 2))

        # BSP room gen
        rooms = []
        attempts = 0
        while len(rooms) < 12 and attempts < 200:
            attempts += 1
            w = random.randint(5, 10)
            h = random.randint(5, 9)
            col = random.randint(1, ARENA_COLS - w - 1)
            row = random.randint(1, ARENA_ROWS - h - 1)
            r = Room(col, row, w, h)
            if any(r.intersects(other) for other in rooms):
                continue
            rooms.append(r)
            for rr in range(row, row + h):
                for cc in range(col, col + w):
                    tm.set(cc, rr, TILE_FLOOR, random.randint(0, 2))

        # Connect rooms with corridors
        for i in range(len(rooms) - 1):
            cx1, cy1 = rooms[i].center()
            cx2, cy2 = rooms[i + 1].center()
            if random.random() < 0.5:
                self._carve_h(tm, cx1, cx2, cy1)
                self._carve_v(tm, cy1, cy2, cx2)
            else:
                self._carve_v(tm, cy1, cy2, cx1)
                self._carve_h(tm, cx1, cx2, cy2)

        self.rooms = rooms

        # Player start in first room center
        if rooms:
            cx, cy = rooms[0].center()
            self.player_start = (cx * SCALED + SCALED // 2, cy * SCALED + SCALED // 2)

        # Spawn points in other rooms
        for room in rooms[1:]:
            cx, cy = room.center()
            self.spawn_points.append((cx * SCALED + SCALED // 2, cy * SCALED + SCALED // 2))

        # Place hazards based on wave
        hazard_budget = min(wave * 3, 30)
        hazard_types = [TILE_LAVA, TILE_SPIKE, TILE_POISON]
        if wave >= 3:
            hazard_types.append(TILE_ICE)
        for _ in range(hazard_budget):
            room = random.choice(rooms[1:]) if len(rooms) > 1 else rooms[0]
            hx = random.randint(room.col + 1, room.col + room.w - 2)
            hy = random.randint(room.row + 1, room.row + room.h - 2)
            ht = random.choice(hazard_types)
            tm.set(hx, hy, ht, random.randint(0, 2))

        # Place crates
        for _ in range(10 + wave * 2):
            room = random.choice(rooms)
            cx2 = random.randint(room.col + 1, room.col + room.w - 2)
            cy2 = random.randint(room.row + 1, room.row + room.h - 2)
            if tm.get(cx2, cy2).type == TILE_FLOOR:
                tm.set(cx2, cy2, TILE_CRATE, random.randint(0, 2))

        # Border walls
        for col in range(ARENA_COLS):
            tm.set(col, 0, TILE_WALL, 0)
            tm.set(col, ARENA_ROWS - 1, TILE_WALL, 0)
        for row in range(ARENA_ROWS):
            tm.set(0, row, TILE_WALL, 0)
            tm.set(ARENA_COLS - 1, row, TILE_WALL, 0)

    def _carve_h(self, tm, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tm.set(x, y, TILE_FLOOR, random.randint(0, 2))
            tm.set(x, y - 1, TILE_FLOOR, random.randint(0, 2))

    def _carve_v(self, tm, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tm.set(x, y, TILE_FLOOR, random.randint(0, 2))
            tm.set(x + 1, y, TILE_FLOOR, random.randint(0, 2))

    def get_random_spawn(self):
        if self.spawn_points:
            return random.choice(self.spawn_points)
        return self.player_start

    def update(self, dt):
        self.tilemap.update(dt)

    def render(self, screen, camera):
        self.tilemap.render(screen, camera)