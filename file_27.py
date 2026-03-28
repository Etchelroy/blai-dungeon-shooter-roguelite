import pygame
import math
import random

_cache = {}

def _make_surface(key, size, draw_fn):
    if key not in _cache:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        draw_fn(surf)
        _cache[key] = surf
    return _cache[key]

def get_player_surf():
    def draw(s):
        pygame.draw.circle(s, (80, 160, 255), (16, 16), 14)
        pygame.draw.circle(s, (200, 230, 255), (16, 16), 10)
        pygame.draw.circle(s, (255,255,255), (20, 12), 4)
    return _make_surface("player", (32, 32), draw)

def get_enemy_surf(etype):
    colors = {
        "grunt": (200, 60, 60),
        "fast": (255, 180, 0),
        "tank": (100, 100, 180),
        "shooter": (180, 60, 180),
        "bomber": (255, 100, 0),
        "shielder": (60, 180, 60),
        "healer": (0, 220, 180),
        "swarm": (220, 180, 50),
        "ghost": (180, 180, 220),
        "elite": (220, 50, 120),
    }
    c = colors.get(etype, (150, 150, 150))
    size = {"tank": 48, "elite": 44}.get(etype, 32)
    def draw(s):
        r = size // 2
        pygame.draw.circle(s, c, (r, r), r - 2)
        pygame.draw.circle(s, (255,255,255), (r, r), r - 2, 2)
    return _make_surface(f"enemy_{etype}", (size, size), draw)

def get_boss_surf(btype, phase=1):
    sizes = {"golem": 96, "hydra": 112, "specter": 88}
    colors = {
        "golem": [(180,120,60),(220,160,80),(255,200,100)],
        "hydra": [(60,180,60),(100,220,80),(150,255,100)],
        "specter": [(100,60,180),(140,80,220),(180,120,255)],
    }
    sz = sizes.get(btype, 96)
    phase_idx = min(phase - 1, 2)
    c = colors.get(btype, [(180,180,180)])[phase_idx]
    def draw(s):
        r = sz // 2
        pygame.draw.circle(s, c, (r, r), r - 2)
        pygame.draw.polygon(s, (255,255,255), [
            (r, 4), (r+12, r-4), (r-12, r-4)
        ])
        pygame.draw.circle(s, (255,255,255), (r, r), r - 2, 3)
    return _make_surface(f"boss_{btype}_p{phase}", (sz, sz), draw)

def get_projectile_surf(ptype):
    configs = {
        "bullet":   ((12, 6),  (255, 240, 100)),
        "pellet":   ((8, 8),   (255, 180, 60)),
        "rail":     ((20, 4),  (0, 255, 255)),
        "grenade":  ((12, 12), (80, 200, 80)),
        "lightning":((10, 10), (255, 255, 0)),
        "boomerang":((18, 8),  (200, 140, 60)),
        "flame":    ((10, 10), (255, 80, 20)),
        "sniper":   ((24, 4),  (200, 200, 255)),
        "enemy_bullet": ((10, 6), (255, 80, 80)),
        "plasma":   ((10, 10), (255, 60, 200)),
    }
    w, h = configs.get(ptype, ((10,6),(200,200,200)))[0]
    c = configs.get(ptype, ((10,6),(200,200,200)))[1]
    def draw(s):
        pygame.draw.ellipse(s, c, (0, 0, w, h))
    return _make_surface(f"proj_{ptype}", (w, h), draw)

def get_tile_surf(ttype):
    configs = {
        "floor":      (60, 60, 70),
        "floor2":     (70, 65, 60),
        "floor3":     (55, 70, 65),
        "wall":       (90, 90, 100),
        "wall2":      (100, 85, 70),
        "lava":       (220, 80, 20),
        "ice":        (150, 210, 255),
        "spikes":     (160, 160, 160),
        "poison":     (80, 200, 80),
        "crate":      (160, 110, 60),
    }
    c = configs.get(ttype, (80, 80, 80))
    def draw(s):
        pygame.draw.rect(s, c, (0, 0, 48, 48))
        pygame.draw.rect(s, (0,0,0,60), (0, 0, 48, 48), 1)
        if ttype == "lava":
            for _ in range(4):
                rx, ry = random.randint(4,40), random.randint(4,40)
                pygame.draw.circle(s, (255,140,0), (rx,ry), random.randint(3,7))
        elif ttype == "ice":
            pygame.draw.line(s, (200,240,255), (8,8), (40,40), 2)
            pygame.draw.line(s, (200,240,255), (40,8), (8,40), 2)
        elif ttype == "spikes":
            for i in range(3):
                x = 8 + i * 16
                pygame.draw.polygon(s, (200,200,200), [(x,42),(x+6,42),(x+3,10)])
        elif ttype == "poison":
            pygame.draw.circle(s, (40,160,40), (24,24), 12)
        elif ttype == "crate":
            pygame.draw.rect(s, (120,80,40), (4,4,40,40), 3)
            pygame.draw.line(s, (120,80,40), (4,4),(44,44), 2)
            pygame.draw.line(s, (120,80,40), (44,4),(4,44), 2)
    return _make_surface(f"tile_{ttype}", (48, 48), draw)

def get_coin_surf(size="small"):
    colors = {"small":(255,220,50),"medium":(255,180,30),"large":(255,150,0)}
    radii = {"small":6,"medium":9,"large":13}
    c = colors.get(size,(255,200,0))
    r = radii.get(size,8)
    def draw(s):
        pygame.draw.circle(s, c, (r,r), r)
        pygame.draw.circle(s, (255,255,200), (r,r), r, 1)
    return _make_surface(f"coin_{size}", (r*2, r*2), draw)

def get_font(size=20):
    key = f"font_{size}"
    if key not in _cache:
        _cache[key] = pygame.font.SysFont("consolas", size, bold=True)
    return _cache[key]