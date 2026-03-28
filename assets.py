import pygame
import math
import random
from constants import *

_cache = {}

def _make_key(*args):
    return str(args)

def get_player_surf():
    key = "player"
    if key not in _cache:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80, 160, 255), (16, 16), 14)
        pygame.draw.circle(surf, (140, 200, 255), (16, 16), 14, 2)
        pygame.draw.circle(surf, (200, 230, 255), (20, 12), 5)
        _cache[key] = surf
    return _cache[key]

def get_enemy_surf(etype, size=32):
    key = f"enemy_{etype}_{size}"
    if key not in _cache:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = {
            "grunt": (220, 80, 80),
            "speeder": (80, 220, 80),
            "tank": (80, 80, 220),
            "sniper": (220, 180, 80),
            "exploder": (220, 120, 40),
            "shield": (100, 100, 220),
            "ghost": (180, 180, 220),
            "swarm": (220, 220, 80),
            "healer": (80, 220, 160),
            "berserker": (220, 40, 40),
        }
        c = colors.get(etype, (180, 80, 180))
        r = size // 2
        pygame.draw.circle(surf, c, (r, r), r - 2)
        pygame.draw.circle(surf, WHITE, (r, r), r - 2, 2)
        eye_x = r + 4
        eye_y = r - 4
        pygame.draw.circle(surf, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(surf, BLACK, (eye_x + 1, eye_y), 2)
        _cache[key] = surf
    return _cache[key]

def get_boss_surf(btype, size=80):
    key = f"boss_{btype}_{size}"
    if key not in _cache:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = {"destroyer": (200, 40, 40), "necromancer": (120, 40, 200), "titan": (40, 120, 200)}
        c = colors.get(btype, (200, 40, 200))
        r = size // 2
        pygame.draw.circle(surf, c, (r, r), r - 2)
        pygame.draw.circle(surf, WHITE, (r, r), r - 2, 3)
        for i in range(6):
            angle = math.radians(i * 60)
            sx = r + int(math.cos(angle) * (r - 8))
            sy = r + int(math.sin(angle) * (r - 8))
            pygame.draw.circle(surf, WHITE, (sx, sy), 5)
        pygame.draw.circle(surf, WHITE, (r - 10, r - 8), 7)
        pygame.draw.circle(surf, RED, (r - 10, r - 8), 5)
        pygame.draw.circle(surf, WHITE, (r + 10, r - 8), 7)
        pygame.draw.circle(surf, RED, (r + 10, r - 8), 5)
        _cache[key] = surf
    return _cache[key]

def get_tile_surf(tile_type):
    key = f"tile_{tile_type}"
    if key not in _cache:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        if tile_type == TILE_FLOOR:
            surf.fill((60, 55, 70))
            for _ in range(8):
                x = random.randint(0, TILE_SIZE - 4)
                y = random.randint(0, TILE_SIZE - 4)
                pygame.draw.rect(surf, (50, 45, 60), (x, y, 3, 3))
        elif tile_type == TILE_FLOOR_ALT:
            surf.fill((50, 65, 55))
            for _ in range(6):
                x = random.randint(0, TILE_SIZE - 4)
                y = random.randint(0, TILE_SIZE - 4)
                pygame.draw.rect(surf, (40, 55, 45), (x, y, 3, 3))
        elif tile_type == TILE_WALL:
            surf.fill((90, 85, 100))
            pygame.draw.rect(surf, (70, 65, 80), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4))
            pygame.draw.line(surf, (110, 105, 120), (0, 0), (TILE_SIZE, 0), 2)
            pygame.draw.line(surf, (110, 105, 120), (0, 0), (0, TILE_SIZE), 2)
        elif tile_type == TILE_WALL_ALT:
            surf.fill((100, 80, 60))
            pygame.draw.rect(surf, (80, 60, 45), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4))
        elif tile_type == TILE_LAVA:
            surf.fill((180, 60, 20))
            for _ in range(5):
                x = random.randint(4, TILE_SIZE - 8)
                y = random.randint(4, TILE_SIZE - 8)
                pygame.draw.circle(surf, (240, 120, 30), (x, y), random.randint(3, 7))
        elif tile_type == TILE_ICE:
            surf.fill((160, 210, 240))
            pygame.draw.line(surf, WHITE, (8, 8), (TILE_SIZE - 8, TILE_SIZE - 8), 2)
            pygame.draw.line(surf, WHITE, (TILE_SIZE - 8, 8), (8, TILE_SIZE - 8), 2)
        elif tile_type == TILE_SPIKES:
            surf.fill((70, 65, 75))
            for i in range(3):
                bx = 4 + i * 14
                pts = [(bx, TILE_SIZE - 4), (bx + 6, TILE_SIZE - 4), (bx + 3, 6)]
                pygame.draw.polygon(surf, (180, 180, 200), pts)
        elif tile_type == TILE_POISON:
            surf.fill((50, 100, 50))
            for _ in range(4):
                x = random.randint(4, TILE_SIZE - 8)
                y = random.randint(4, TILE_SIZE - 8)
                pygame.draw.circle(surf, (80, 180, 60), (x, y), random.randint(3, 6))
        elif tile_type == TILE_CRATE:
            surf.fill((140, 90, 40))
            pygame.draw.rect(surf, (110, 70, 25), (3, 3, TILE_SIZE - 6, TILE_SIZE - 6))
            pygame.draw.line(surf, (80, 50, 15), (TILE_SIZE // 2, 2), (TILE_SIZE // 2, TILE_SIZE - 2), 2)
            pygame.draw.line(surf, (80, 50, 15), (2, TILE_SIZE // 2), (TILE_SIZE - 2, TILE_SIZE // 2), 2)
            pygame.draw.rect(surf, (160, 110, 50), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        else:
            surf.fill((80, 80, 80))
        _cache[key] = surf
    return _cache[key]

def get_projectile_surf(ptype, size=8):
    key = f"proj_{ptype}_{size}"
    if key not in _cache:
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        colors = {
            "bullet": YELLOW, "pellet": ORANGE, "sniper": CYAN,
            "rocket": ORANGE, "chain": PURPLE, "boomerang": TEAL,
            "flame": RED, "enemy": RED, "boss": (255, 80, 80),
        }
        c = colors.get(ptype, WHITE)
        pygame.draw.circle(surf, c, (size, size), size - 1)
        pygame.draw.circle(surf, WHITE, (size, size), size - 1, 1)
        _cache[key] = surf
    return _cache[key]

def get_coin_surf(coin_type):
    key = f"coin_{coin_type}"
    if key not in _cache:
        sizes = {"small": 8, "medium": 12, "large": 16}
        colors = {"small": YELLOW, "medium": GOLD, "large": ORANGE}
        sz = sizes.get(coin_type, 10)
        surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, colors.get(coin_type, GOLD), (sz, sz), sz - 1)
        pygame.draw.circle(surf, WHITE, (sz, sz), sz - 1, 1)
        _cache[key] = surf
    return _cache[key]

def get_font(size=24):
    key = f"font_{size}"
    if key not in _cache:
        try:
            _cache[key] = pygame.font.SysFont("consolas", size, bold=True)
        except:
            _cache[key] = pygame.font.Font(None, size)
    return _cache[key]