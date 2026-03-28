import pygame, random, math
from settings import TILE_SIZE, ARENA_W, ARENA_H

FLOOR=0; WALL=1; LAVA=2; ICE=3; SPIKE=4; VENT=5; VOID=6

TILE_COLORS = {
    FLOOR: (60,55,50),
    WALL:  (40,35,80),
    LAVA:  (200,80,20),
    ICE:   (140,200,230),
    SPIKE: (90,90,90),
    VENT:  (50,80,60),
    VOID:  (10,10,15),
}

TILE_VARIANT_COLORS = {
    FLOOR: [(55,50,45),(60,55,50),(65,60,55),(58,53,48)],
    WALL:  [(35,30,75),(40,35,80),(45,40,85),(38,33,78)],
}

class Tile:
    __slots__=['type','variant','damage','slippery','effect_timer']
    def __init__(self, t, variant=0):
        self.type=t; self.variant=variant
        self.damage = 0
        self.slippery = False
        self.effect_timer = 0.0

class Tilemap:
    def __init__(self):
        self.cols = ARENA_W // TILE_SIZE
        self.rows = ARENA_H // TILE_SIZE
        self.tiles = [[Tile(FLOOR) for _ in range(self.cols)] for _ in range(self.rows)]
        self._cache = {}
        self._tile_surfs = {}
        self._build_tile_surfs()

    def _build_tile_surfs(self):
        for t, variants in [(FLOOR, 4),(WALL,4)]:
            for v in range(variants):
                s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                base = TILE_VARIANT_COLORS.get(t, [TILE_COLORS[t]])[v % len(TILE_VARIANT_COLORS.get(t,[TILE_COLORS[t]]))]
                s.fill(base)
                # add some noise detail
                for _ in range(6):
                    px = random.randint(0,TILE_SIZE-2)
                    py = random.randint(0,TILE_SIZE-2)
                    dc = random.randint(-15,15)
                    col = tuple(max(0,min(255,c+dc)) for c in base)
                    pygame.draw.rect(s, col, (px,py,2,2))
                self._tile_surfs[(t,v)] = s
        for t in [LAVA,ICE,SPIKE,VENT,VOID]:
            s = pygame.Surface((TILE_SIZE,TILE_SIZE))
            s.fill(TILE_COLORS[t])
            if t==LAVA:
                for _ in range(4):
                    pygame.draw.circle(s,(220,120,20),
                        (random.randint(2,TILE_SIZE-2),random.randint(2,TILE_SIZE-2)),2)
            elif t==SPIKE:
                pygame.draw.polygon(s,(120,120,120),[(8,0),(14,16),(2,16)])
            elif t==VENT:
                pygame.draw.ellipse(s,(80,120,90),(4,4,8,8))
            self._tile_surfs[(t,0)] = s

    def get(self, col, row):
        if 0<=row<self.rows and 0<=col<self.cols:
            return self.tiles[row][col]
        return Tile(WALL)

    def set(self, col, row, tile_type, variant=0):
        if 0<=row<self.rows and 0<=col<self.cols:
            t = Tile(tile_type, variant)
            if tile_type==ICE: t.slippery=True
            if tile_type==LAVA: t.damage=15
            if tile_type==SPIKE: t.damage=8
            self.tiles[row][col] = t

    def is_solid(self, col, row):
        t = self.get(col, row)
        return t.type in (WALL, VOID)

    def is_solid_world(self, wx, wy):
        return self.is_solid(int(wx//TILE_SIZE), int(wy//TILE_SIZE))

    def draw(self, surf, cam_x, cam_y, anim_t=0):
        ts = TILE_SIZE
        startc = max(0, int(cam_x//ts))
        endc = min(self.cols, int((cam_x+surf.get_width())//ts)+2)
        startr = max(0, int(cam_y//ts))
        endr = min(self.rows, int((cam_y+surf.get_height())//ts)+2)
        for r in range(startr, endr):
            for c in range(startc, endc):
                tile = self.tiles[r][c]
                sx = c*ts - int(cam_x)
                sy = r*ts - int(cam_y)
                key = (tile.type, tile.variant)
                if key in self._tile_surfs:
                    s = self._tile_surfs[key]
                    if tile.type==LAVA:
                        # animate lava flicker
                        s2 = s.copy()
                        dc = int(20*math.sin(anim_t*3 + c*0.5 + r*0.7))
                        s2.fill((dc,dc//2,0), special_flags=pygame.BLEND_RGB_ADD)
                        surf.blit(s2,(sx,sy))
                    else:
                        surf.blit(s,(sx,sy))
                else:
                    pygame.draw.rect(surf, TILE_COLORS.get(tile.type,(80,80,80)),(sx,sy,ts,ts))

    def update_effects(self, dt, entities):
        for e in entities:
            c = int(e.x // TILE_SIZE)
            r = int(e.y // TILE_SIZE)
            tile = self.get(c, r)
            if tile.type == LAVA:
                e.take_damage(tile.damage * dt, 'lava')
            elif tile.type == SPIKE:
                e.take_damage(tile.damage * dt, 'spike')
            elif tile.type == ICE:
                e.slipping = True
            elif tile.type == VENT:
                e.vx += 0; e.vy -= 60*dt  # upward push