import random, math
from src.tilemap import Tilemap, FLOOR, WALL, LAVA, ICE, SPIKE, VENT, VOID
from settings import TILE_SIZE, ARENA_W, ARENA_H

class Room:
    def __init__(self, c, r, w, h):
        self.c=c; self.r=r; self.w=w; self.h=h
    def center(self):
        return self.c+self.w//2, self.r+self.h//2
    def intersects(self, other, margin=1):
        return (self.c - margin < other.c+other.w and
                self.c+self.w+margin > other.c and
                self.r - margin < other.r+other.h and
                self.r+self.h+margin > other.r)

class ArenaGenerator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def generate(self, wave=1):
        tm = Tilemap()
        cols, rows = tm.cols, tm.rows
        # fill all walls
        for r in range(rows):
            for c in range(cols):
                tm.set(c, r, WALL, self.rng.randint(0,3))

        rooms = []
        attempts = 80
        for _ in range(attempts):
            w = self.rng.randint(6,14)
            h = self.rng.randint(6,12)
            c = self.rng.randint(2, cols-w-2)
            r = self.rng.randint(2, rows-h-2)
            room = Room(c,r,w,h)
            if not any(room.intersects(ex) for ex in rooms):
                rooms.append(room)
                self._carve_room(tm, room)

        # corridors
        for i in range(len(rooms)-1):
            self._connect(tm, rooms[i], rooms[i+1])

        # border walls
        for r in range(rows):
            tm.set(0,r,WALL); tm.set(cols-1,r,WALL)
        for c in range(cols):
            tm.set(c,0,WALL); tm.set(c,rows-1,WALL)

        # hazards based on wave
        hazard_count = min(3+wave, 12)
        hazards = [LAVA,ICE,SPIKE,VENT]
        for _ in range(hazard_count):
            if len(rooms) > 2:
                room = self.rng.choice(rooms[1:])
                htype = self.rng.choice(hazards)
                self._carve_hazard(tm, room, htype)

        # crates (stored as list of world positions)
        crates = []
        for room in rooms:
            if self.rng.random() < 0.5:
                cx = (room.c + self.rng.randint(1,room.w-2)) * TILE_SIZE + TILE_SIZE//2
                cy = (room.r + self.rng.randint(1,room.h-2)) * TILE_SIZE + TILE_SIZE//2
                crates.append([cx, cy, 30])  # x,y,hp

        spawn = rooms[0].center() if rooms else (cols//2, rows//2)
        spawn_world = (spawn[0]*TILE_SIZE + TILE_SIZE//2, spawn[1]*TILE_SIZE + TILE_SIZE//2)

        enemy_spawns = []
        for room in rooms[1:]:
            ec = room.center()
            enemy_spawns.append((ec[0]*TILE_SIZE+TILE_SIZE//2, ec[1]*TILE_SIZE+TILE_SIZE//2))

        return tm, spawn_world, enemy_spawns, crates

    def _carve_room(self, tm, room):
        for r in range(room.r, room.r+room.h):
            for c in range(room.c, room.c+room.w):
                tm.set(c, r, FLOOR, tm.rng.randint(0,3) if hasattr(tm,'rng') else 0)

    def _connect(self, tm, a, b):
        ac, ar = a.center()
        bc, br = b.center()
        # horizontal then vertical
        cc, cr = ac, ar
        while cc != bc:
            cc += 1 if bc > cc else -1
            tm.set(cc, cr, FLOOR, 0)
            tm.set(cc, cr+1, FLOOR, 0)
        while cr != br:
            cr += 1 if br > cr else -1
            tm.set(cc, cr, FLOOR, 0)
            tm.set(cc+1, cr, FLOOR, 0)

    def _carve_hazard(self, tm, room, htype):
        # place a small patch of hazard tiles
        rng = self.rng
        sw = rng.randint(2,min(4,room.w-2))
        sh = rng.randint(2,min(3,room.h-2))
        sc = rng.randint(room.c+1, room.c+room.w-sw-1)
        sr = rng.randint(room.r+1, room.r+room.h-sh-1)
        for r in range(sr, sr+sh):
            for c in range(sc, sc+sw):
                tm.set(c, r, htype, 0)