import pygame
import math
import random
from constants import *
from utils import normalize, distance, clamp
import assets

class Afterimage:
    def __init__(self, x, y, angle, surf):
        self.x = x; self.y = y
        self.angle = angle
        self.surf = surf
        self.alpha = 160
        self.life = 0.2

    def update(self, dt):
        self.life -= dt
        self.alpha = int(160 * max(0, self.life / 0.2))
        return self.life > 0

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        s = self.surf.copy()
        s.set_alpha(self.alpha)
        rotated = pygame.transform.rotate(s, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(sx, sy))
        surface.blit(rotated, rect)

class Player:
    def __init__(self, x, y, secondary_ability=None):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.alive = True

        self.dash_cooldown = PLAYER_DASH_COOLDOWN
        self._dash_timer = 0.0
        self._dash_active = False
        self._dash_duration = PLAYER_DASH_DURATION
        self._dash_vx = 0.0
        self._dash_vy = 0.0
        self.iframe_timer = 0.0

        self.melee_cooldown = PLAYER_MELEE_COOLDOWN
        self._melee_timer = 0.0
        self.melee_active = False
        self.melee_timer_active = 0.0

        self.shielded = False
        self.shield_timer = 0.0
        self.slow_timer = 0.0
        self.slow_factor = 1.0
        self.adrenaline_timer = 0.0

        self.secondary = secondary_ability
        self.afterimages = []

        self.surf = assets.get_player_surf()
I'll analyze what's needed and implement the remaining files. Based on the shifts completed, I need: enemies.py, bosses.py, arena.py, hud.py, menu.py, wave_manager.py, coins.py, game.py, and main.py.

```python
# filename: constants.py
import pygame

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "Dungeon Shooter Roguelite"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 50, 220)
CYAN = (0, 220, 220)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
DARK_RED = (140, 20, 20)
DARK_GREEN = (20, 100, 20)
DARK_BLUE = (20, 30, 100)
PINK = (255, 100, 180)
BROWN = (139, 90, 43)
GOLD = (255, 200, 0)
LAVA_COLOR = (200, 60, 0)
ICE_COLOR = (180, 230, 255)
POISON_COLOR = (100, 200, 50)
SPIKE_COLOR = (160, 160, 160)

# Tile types
TILE_FLOOR = 0
TILE_WALL = 1
TILE_LAVA = 2
TILE_ICE = 3
TILE_SPIKE = 4
TILE_POISON = 5
TILE_CRATE = 6

TILE_SIZE = 64

# Player
PLAYER_SPEED = 220
PLAYER_FRICTION = 0.82
PLAYER_DASH_SPEED = 600
PLAYER_DASH_DURATION = 0.15
PLAYER_DASH_COOLDOWN = 1.2
PLAYER_DASH_IFRAMES = 0.2
PLAYER_MAX_HP = 100
PLAYER_MELEE_RANGE = 70
PLAYER_MELEE_DAMAGE = 35
PLAYER_MELEE_COOLDOWN = 0.5

# Weapons
WEAPON_PISTOL = 0
WEAPON_SHOTGUN = 1
WEAPON_RIFLE = 2
WEAPON_LAUNCHER = 3
WEAPON_SNIPER = 4
WEAPON_FLAMETHROWER = 5
WEAPON_CHAIN = 6
WEAPON_BOOMERANG = 7

WEAPON_NAMES = ["Pistol", "Shotgun", "Rifle", "Launcher", "Sniper", "Flamethrower", "Chain", "Boomerang"]

# Secondary abilities
SEC_SHIELD = 0
SEC_TURRET = 1
SEC_AIRSTRIKE = 2
SEC_FREEZE = 3
SEC_VAMPIRIC = 4
SEC_DECOY = 5

SEC_NAMES = ["Shield", "Turret", "Airstrike", "Freeze", "Vampiric", "Decoy"]

# Enemy tiers
TIER1 = 1
TIER2 = 2
TIER3 = 3

# Layers / z-order (draw order)
LAYER_FLOOR = 0
LAYER_HAZARD = 1
LAYER_CRATE = 2
LAYER_ENEMY = 3
LAYER_PLAYER = 4
LAYER_PROJECTILE = 5
LAYER_PARTICLE = 6
LAYER_HUD = 7

# Combo
COMBO_TIMEOUT = 3.0