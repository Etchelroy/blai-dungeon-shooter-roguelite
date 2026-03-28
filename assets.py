import pygame, math, random
from constants import *

_cache = {}

def _key(*args):
    return args

def get_player_surf():
    k = "player"
    if k not in _cache:
        s = pygame.Surface((32,32), pygame.SRCALPHA)
        pygame.draw.polygon(s, (80,180,80), [(16,2),(30,30),(2,30)])
        pygame.draw.circle(s, (120,220,120), (16,12), 8)
        _cache[k] = s
    return _cache[k]

def get_enemy_surf(etype, size=32):
    k = f"enemy_{etype}_{size}"
    if k not in _cache:
        s = pygame.Surface((size,size), pygame.SRCALPHA)
        colors = {
            "goblin":   (80,180,60),
            "skeleton": (220,220,200),
            "bat":      (100,60,140),
            "slime":    (60,200,100),
            "orc":      (60,140,60),
            "mage":     (140,60,200),
            "archer":   (180,140,60),
            "knight":   (160,160,180),
            "demon":    (200,40,40),
            "golem":    (140,120,80),
        }
        c = colors.get(etype, (200,100,100))
        pygame.draw.circle(s, c, (size//2,size//2), size//2-2)
        pygame.draw.circle(s, (255,255,255), (size//3, size//3), size//8)
        pygame.draw.circle(s, (255,255,255), (2*size//3, size//3), size//8)
        _cache[k] = s
    return _cache[k]

def get_boss_surf(btype, size=80):
    k = f"boss_{btype}_{size}"
    if k not in _cache:
        s = pygame.Surface((size,size), pygame.SRCALPHA)
        colors = {"lich":(120,60,200),"dragon":(200,60,60),"titan":(80,80,200)}
        c = colors.get(btype, (200,50,50))
        pygame.draw.circle(s, c, (size//2,size//2), size//2-2)
        pygame.draw.rect(s, (255,255,255), (size//4, size//3, size//2, size//6))
        for i in range(3):
            px = size//4 + i*(size//6)
            pygame.draw.line(s, (255,220,0), (px, 2), (px+size//8, size//3), 3)
        _cache[k] = s
    return _cache[k]

def get_tile_surf(ttype):
    k = f"tile_{ttype}"
    if k not in _cache:
        s = pygame.Surface((TILE, TILE))
        palettes = {
            T_FLOOR:  (50,45,40),
            T_WALL:   (30,30,35),
            T_LAVA:   (200,80,20),
            T_ICE:    (160,210,240),
            T_SPIKES: (80,80,90),
            T_POISON: (40,120,40),
            T_CRATE:  (140,90,40),
            T_EMPTY:  (10,10,10),
        }
        base = palettes.get(ttype, (60,60,60))
        s.fill(base)
        if ttype == T_WALL:
            for _ in range(6):
                rx = random.randint(0,TILE-4)
                ry = random.randint(0,TILE-4)
                pygame.draw.rect(s,(20,20,25),(rx,ry,random.randint(2,6),random.randint(2,6)))
        elif ttype == T_FLOOR:
            for _ in range(4):
                rx = random.randint(0,TILE-3)
                ry = random.randint(0,TILE-3)
                pygame.draw.rect(s,(45,40,35),(rx,ry,random.randint(1,4),random.randint(1,4)))
        elif ttype == T_LAVA:
            for _ in range(5):
                rx = random.randint(2,TILE-6)
                ry = random.randint(2,TILE-6)
                pygame.draw.circle(s,(255,160,0),(rx,ry),random.randint(2,5))
        elif ttype == T_SPIKES:
            for i in range(3):
                x = 6 + i*14
                pygame.draw.polygon(s,(200,200,210),[(x,TILE-4),(x+6,TILE-4),(x+3,4)])
        elif ttype == T_CRATE:
            pygame.draw.rect(s,(160,110,60),(4,4,TILE-8,TILE-8),2)
            pygame.draw.line(s,(160,110,60),(4,4),(TILE-4,TILE-4),1)
            pygame.draw.line(s,(160,110,60),(TILE-4,4),(4,TILE-4),1)
        _cache[k] = s
    return _cache[k]

def get_projectile_surf(color, size=8):
    k = f"proj_{color}_{size}"
    if k not in _cache:
        s = pygame.Surface((size,size), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (size//2,size//2), size//2)
        _cache[k] = s
    return _cache[k]

def get_coin_surf():
    k = "coin"
    if k not in _cache:
        s = pygame.Surface((16,16), pygame.SRCALPHA)
        pygame.draw.circle(s, GOLD, (8,8), 7)
        pygame.draw.circle(s, YELLOW, (8,8), 5)
        _cache[k] = s
    return _cache[k]

def clear_cache():
    _cache.clear()