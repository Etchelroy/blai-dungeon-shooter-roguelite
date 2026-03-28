import pygame
import math
import random
from constants import *

_surf_cache = {}

def _make_key(*args):
    return args

def get_player_surf(size=28):
    key = ('player', size)
    if key not in _surf_cache:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, (80,180,255), (size//2, size//2), size//2)
        pygame.draw.circle(s, (200,230,255), (size//2, size//2), size//2, 2)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_enemy_surf(etype, size=24):
    key = ('enemy', etype, size)
    if key not in _surf_cache:
        colors = {
            'grunt': (180,50,50),
            'speeder': (50,180,50),
            'tank': (100,100,200),
            'shooter': (200,150,50),
            'splitter': (180,50,180),
            'bomber': (220,120,30),
            'shield': (80,180,200),
            'vampire': (140,30,140),
            'ghost': (200,200,220),
            'titan': (60,60,60),
        }
        col = colors.get(etype, (150,150,150))
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        if etype == 'tank':
            pygame.draw.rect(s, col, (2, 2, size-4, size-4))
            pygame.draw.rect(s, WHITE, (2, 2, size-4, size-4), 2)
        elif etype == 'ghost':
            pygame.draw.circle(s, col + (160,), (size//2, size//2), size//2)
        else:
            pygame.draw.circle(s, col, (size//2, size//2), size//2)
            pygame.draw.circle(s, WHITE, (size//2, size//2), size//2, 2)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_boss_surf(boss_id, phase, size=64):
    key = ('boss', boss_id, phase, size)
    if key not in _surf_cache:
        colors = [(200,50,50),(220,100,30),(240,200,0)]
        col = colors[min(phase, 2)]
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (size//2, size//2), size//2)
        pygame.draw.circle(s, WHITE, (size//2, size//2), size//2, 3)
        # phase marking
        for i in range(phase+1):
            angle = math.pi/2 + i * (math.pi*2/3)
            px = size//2 + int(math.cos(angle)*(size//2-8))
            py = size//2 + int(math.sin(angle)*(size//2-8))
            pygame.draw.circle(s, WHITE, (px, py), 4)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_tile_surf(tile_type):
    key = ('tile', tile_type)
    if key not in _surf_cache:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        if tile_type == TILE_FLOOR:
            s.fill((60,55,50))
            for _ in range(6):
                rx, ry = random.randint(0, TILE_SIZE-4), random.randint(0, TILE_SIZE-4)
                pygame.draw.rect(s, (55,50,45), (rx, ry, 3, 3))
        elif tile_type == TILE_WALL:
            s.fill((90,85,80))
            pygame.draw.rect(s, (70,65,60), (0,0,TILE_SIZE,TILE_SIZE), 3)
        elif tile_type == TILE_LAVA:
            s.fill(LAVA_COLOR)
            pygame.draw.circle(s, (240,100,0), (16,16), 10)
            pygame.draw.circle(s, (240,100,0), (48,48), 8)
        elif tile_type == TILE_ICE:
            s.fill(ICE_COLOR)
            pygame.draw.line(s, WHITE, (0,0),(TILE_SIZE,TILE_SIZE), 1)
            pygame.draw.line(s, WHITE, (TILE_SIZE,0),(0,TILE_SIZE), 1)
        elif tile_type == TILE_SPIKE:
            s.fill((50,50,55))
            for i in range(4):
                x = 8 + i*16
                pts = [(x,TILE_SIZE-4),(x+8,TILE_SIZE-4),(x+4,4)]
                pygame.draw.polygon(s, SPIKE_COLOR, pts)
        elif tile_type == TILE_POISON:
            s.fill((30,60,30))
            pygame.draw.circle(s, POISON_COLOR, (32,32), 20)
            pygame.draw.circle(s, (80,160,40), (32,32), 20, 2)
        elif tile_type == TILE_CRATE:
            s.fill(BROWN)
            pygame.draw.rect(s, (100,60,20), (0,0,TILE_SIZE,TILE_SIZE), 3)
            pygame.draw.line(s, (100,60,20),(0,0),(TILE_SIZE,TILE_SIZE),2)
            pygame.draw.line(s, (100,60,20),(TILE_SIZE,0),(0,TILE_SIZE),2)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_projectile_surf(ptype, size=8):
    key = ('proj', ptype, size)
    if key not in _surf_cache:
        colors = {
            'bullet': YELLOW,
            'pellet': ORANGE,
            'rocket': RED,
            'flame': (255,100,0),
            'chain': CYAN,
            'boomerang': (200,200,100),
            'enemy': (255,80,80),
            'boss': (255,0,200),
            'sniper': (200,255,200),
        }
        col = colors.get(ptype, WHITE)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (size//2, size//2), size//2)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_coin_surf(size=12):
    key = ('coin', size)
    if key not in _surf_cache:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(s, GOLD, (size//2, size//2), size//2)
        pygame.draw.circle(s, YELLOW, (size//2, size//2), size//2-2)
        _surf_cache[key] = s
    return _surf_cache[key]

def get_font(size=20):
    key = ('font', size)
    if key not in _surf_cache:
        try:
            f = pygame.font.SysFont('consolas', size, bold=True)
        except:
            f = pygame.font.Font(None, size)
        _surf_cache[key] = f
    return _surf_cache[key]