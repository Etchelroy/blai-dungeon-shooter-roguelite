import pygame
from settings import *

_cache = {}

def preload_assets():
    draw_all()

def get(key):
    return _cache.get(key)

def _surf(w, h, alpha=True):
    s = pygame.Surface((w, h), pygame.SRCALPHA if alpha else 0)
    s.fill((0,0,0,0) if alpha else (0,0,0))
    return s

def cache(key, surf):
    _cache[key] = surf
    return surf

def draw_all():
    draw_tiles()
    draw_player_sprites()
    draw_enemy_sprites()
    draw_boss_sprites()
    draw_weapon_icons()
    draw_projectile_sprites()
    draw_ui_elements()
    draw_loot_sprites()

def draw_tiles():
    ts = TILE_SIZE_SCALED
    for variant in range(4):
        s = _surf(ts, ts, False)
        base = (55+variant*3, 48+variant*2, 42+variant*2)
        s.fill(base)
        if variant % 2 == 0:
            pygame.draw.line(s, (45,38,32), (0, ts//2), (ts, ts//2), 1)
        cache(f"tile_floor_{variant}", s)

    for variant in range(4):
        s = _surf(ts, ts, False)
        s.fill((75+variant*2, 65+variant*2, 55+variant*2))
        pygame.draw.rect(s, (60,50,40), (0,0,ts,4))
        pygame.draw.rect(s, (60,50,40), (0,0,4,ts))
        pygame.draw.rect(s, (90,80,65), (0,0,ts,2))
        cache(f"tile_wall_{variant}", s)

    for t_type, color, name in [
        (TILE_LAVA, (220,80,20), "lava"),
        (TILE_ICE,  (140,200,240), "ice"),
        (TILE_POISON, (60,160,60), "poison"),
    ]:
        s = _surf(ts, ts, False)
        s.fill(color)
        for i in range(0, ts, ts//4):
            c2 = tuple(max(0,min(255,x+20)) for x in color)
            pygame.draw.circle(s, c2, (i+ts//8, ts//2), ts//8)
        cache(f"tile_{name}", s)

    s = _surf(ts, ts, False)
    s.fill((55,48,42))
    pygame.draw.rect(s, (130,90,50), (4,4,ts-8,ts-8))
    pygame.draw.rect(s, (160,110,60), (5,5,ts-10,3))
    pygame.draw.line(s, (100,70,40), (ts//2,4), (ts//2,ts-4), 2)
    pygame.draw.line(s, (100,70,40), (4,ts//2), (ts-4,ts//2), 2)
    cache("tile_crate", s)

    s = _surf(ts, ts, False)
    s.fill((55,48,42))
    for i in range(0, ts, ts//4):
        pygame.draw.polygon(s, (160,160,170), [(i+ts//8,ts-4),(i+ts//4,ts//3),(i+3*ts//8,ts-4)])
    cache("tile_spike", s)

def draw_player_sprites():
    ts = 36
    for frame in range(4):
        s = _surf(ts, ts)
        offset = frame * 2
        body_color = C_PLAYER
        pygame.draw.ellipse(s, C_PLAYER2, (6,8+offset%2,ts-12,ts-14))
        pygame.draw.ellipse(s, body_color, (8,6,ts-16,ts-12))
        pygame.draw.circle(s, (220,200,160), (ts//2, ts//2-2), 8)
        pygame.draw.circle(s, (180,160,120), (ts//2-1, ts//2-3), 7)
        pygame.draw.rect(s, (60,80,140), (ts//2+2, ts//2-1, 12, 5))
        pygame.draw.circle(s, (255,255,200), (ts//2-2, ts//2-4), 2)
        pygame.draw.circle(s, (255,255,200), (ts//2+2, ts//2-4), 2)
        cache(f"player_idle_{frame}", s)

    for frame in range(4):
        s = _surf(ts, ts)
        lean = (frame - 1) * 2
        pygame.draw.ellipse(s, C_PLAYER2, (6+lean,8,ts-12,ts-14))
        pygame.draw.ellipse(s, C_PLAYER, (8+lean,6,ts-16,ts-12))
        pygame.draw.circle(s, (220,200,160), (ts//2+lean, ts//2-2), 8)
        pygame.draw.rect(s, (60,80,140), (ts//2+lean+2, ts//2-1, 12, 5))
        cache(f"player_walk_{frame}", s)

    s = _surf(ts, ts)
    for i in range(6):
        alpha_val = 180 - i*25
        ghost = _surf(ts, ts)
        pygame.draw.ellipse(ghost, (*C_PLAYER, alpha_val), (4,4,ts-8,ts-8))
        s.blit(ghost, (0,0))
    pygame.draw.ellipse(s, (*C_PLAYER, 220), (6,6,ts-12,ts-12))
    cache("player_dash", s)

    s = _surf(ts+8, ts)
    pygame.draw.ellipse(s, C_PLAYER, (8,6,ts-16,ts-12))
    pygame.draw.circle(s, (220,200,160), (ts//2, ts//2-2), 8)
    arc_rect = pygame.Rect(ts//2-4, ts//2-8, 20, 16)
    pygame.draw.arc(s, (200,180,100), arc_rect, -0.5, 0.5, 4)
    cache("player_melee", s)

def draw_enemy_sprites():
    for etype in range(10):
        colors = [
            (C_ENEMY1, (150,30,30)),
            (C_ENEMY2, (130,70,20)),
            (C_ENEMY3, (100,40,140)),
            ((60,180,60),(30,120,30)),
            ((180,180,40),(120,120,20)),
            ((40,120,200),(20,80,150)),
            ((200,100,40),(150,60,20)),
            ((160,40,160),(110,20,110)),
            ((40,180,160),(20,130,110)),
            ((220,160,40),(170,110,20)),
        ]
        c1, c2 = colors[etype % len(colors)]
        for frame in range(4):
            s = _surf(32, 32)
            offset = frame % 2
            size = 24 + (etype % 3) * 2
            x0 = 16 - size//2
            y0 = 16 - size//2 + offset
            pygame.draw.ellipse(s, c2, (x0, y0, size, size))
            pygame.draw.ellipse(s, c1, (x0, y0-1, size, size-2))
            eyes_y = y0 + size//4
            pygame.draw.circle(s, (240,240,240), (x0+size//3, eyes_y), 3)
            pygame.draw.circle(s, (240,240,240), (x0+2*size//3, eyes_y), 3)
            pygame.draw.circle(s, (30,20,20), (x0+size//3, eyes_y), 1)
            pygame.draw.circle(s, (30,20,20), (x0+2*size//3, eyes_y), 1)
            cache(f"enemy_{etype}_frame_{frame}", s)

    for etype in range(10):
        s = _surf(32, 32)
        colors = [(C_ENEMY1,(150,30,30)),(C_ENEMY2,(130,70,20)),(C_ENEMY3,(100,40,140)),
                  ((60,180,60),(30,120,30)),((180,180,40),(120,120,20)),((40,120,200),(20,80,150)),
                  ((200,100,40),(150,60,20)),((160,40,160),(110,20,110)),
                  ((40,180,160),(20,130,110)),((220,160,40),(170,110,20))]
        c1, c2 = colors[etype % len(colors)]
        for i in range(8):
            angle = i * 45
            import math
            rx = 16 + int(12 * math.cos(math.radians(angle)))
            ry = 16 + int(12 * math.sin(math.radians(angle)))
            pygame.draw.circle(s, c1, (rx, ry), 3)
        pygame.draw.circle(s, c2, (16,16), 8)
        cache(f"enemy_{etype}_death", s)

def draw_boss_sprites():
    for boss_id in range(3):
        colors = [(180,30,30),(30,30,200),(160,30,160)]
        c = colors[boss_id]
        sizes = [64, 72, 68]
        sz = sizes[boss_id]
        for phase in range(3):
            for frame in range(6):
                s = _surf(sz, sz)
                darken = phase * 20
                bc = tuple(max(0, x - darken) for x in c)
                offset = frame % 2
                pygame.draw.ellipse(s, tuple(max(0,x-30) for x in bc), (4, 4+offset, sz-8, sz-8))
                pygame.draw.ellipse(s, bc, (4, 2, sz-8, sz-8))
                eyes_y = sz//3
                eye_size = 5 + phase
                for ex in [sz//3, 2*sz//3]:
                    pygame.draw.circle(s, (255,255,100), (ex, eyes_y), eye_size)
                    pygame.draw.circle(s, (20,10,10), (ex, eyes_y), eye_size//2)
                if phase > 0:
                    for i in range(phase * 2):
                        import math
                        ax = sz//2 + int((sz//2-4)*math.cos(math.radians(i*45+frame*10)))
                        ay = sz//2 + int((sz//2-4)*math.sin(math.radians(i*45+frame*10)))
                        pygame.draw.circle(s, (255,200,50), (ax, ay), 3)
                cache(f"boss_{boss_id}_phase_{phase}_frame_{frame}", s)

def draw_weapon_icons():
    names = WEAPON_NAMES
    colors = [(200,200,60),(200,120,60),(80,200,80),(60,80,220),
              (220,100,30),(180,60,180),(60,180,220),(200,160,60)]
    for i, (name, color) in enumerate(zip(names, colors)):
        s = _surf(32, 16)
        pygame.draw.rect(s, color, (0, 4, 28, 8), border_radius=3)
        pygame.draw.circle(s, tuple(max(0,x-40) for x in color), (28, 8), 4)
        pygame.draw.rect(s, tuple(max(0,x-60) for x in color), (8,2,6,12))
        cache(f"weapon_{name}", s)

def draw_projectile_sprites():
    projs = {
        "bullet":     ((255,240,100), 6, 3),
        "shotgun":    ((255,180,80),  5, 3),
        "rifle":      ((100,220,255), 8, 2),
        "plasma":     ((80,100,255),  8, 8),
        "grenade":    ((100,200,80),  8, 8),
        "chain":      ((200,80,255),  6, 4),
        "boomerang":  ((255,200,60),  12,12),
        "flame":      ((255,120,20),  8, 6),
        "enemy":      ((220,60,60),   6, 4),
        "boss":       ((255,40,40),   10,10),
    }
    for name, (color, w, h) in projs.items():
        s = _surf(w, h)
        if w == h:
            pygame.draw.ellipse(s, color, (0,0,w,h))
        else:
            pygame.draw.ellipse(s, color, (0,0,w,h))
            pygame.draw.ellipse(s, (255,255,255,80), (1,1,w-2,h-2))
        cache(f"proj_{name}", s)

def draw_ui_elements():
    s = _surf(200, 20, False)
    s.fill((30,25,35))
    pygame.draw.rect(s, (50,40,60), (0,0,200,20), 2)
    cache("hp_bar_bg", s)

    s = _surf(16, 16)
    pygame.draw.polygon(s, (255,215,0), [(8,1),(10,6),(16,6),(11,10),(13,15),(8,11),(3,15),(5,10),(0,6),(6,6)])
    cache("coin_icon", s)

def draw_loot_sprites():
    s = _surf(12, 12)
    pygame.draw.circle(s, C_COIN, (6,6), 5)
    pygame.draw.circle(s, (255,240,100), (5,5), 2)
    cache("coin", s)

    s = _surf(12, 12)
    pygame.draw.circle(s, (200,60,60), (6,6), 5)
    pygame.draw.circle(s, (240,100,100), (5,5), 2)
    cache("hp_pickup", s)

    s = _surf(12, 12)
    pygame.draw.circle(s, (80,180,255), (6,6), 5)
    pygame.draw.circle(s, (140,220,255), (5,5), 2)
    cache("ammo_pickup", s)