import pygame
import math
import random
from constants import *
from utils import angle_to, vec_from_angle, distance
from projectiles import Projectile
from particles import ParticleSystem

class SecondaryBase:
    def __init__(self, name, sec_id, cooldown):
        self.name = name; self.sec_id = sec_id
        self.cooldown = cooldown; self.timer = 0.0
        self.active = False; self.active_timer = 0.0

    def update(self, dt, player, enemies, projectiles, particles, camera):
        self.timer = max(0, self.timer - dt)

    def can_use(self):
        return self.timer <= 0

    def use(self, player, enemies, projectiles, particles, camera):
        pass

    @property
    def cooldown_fraction(self):
        return 1.0 - (self.timer / self.cooldown) if self.cooldown > 0 else 1.0

class Shield(SecondaryBase):
    def __init__(self):
        super().__init__("Shield", SEC_SHIELD, 8.0)
        self.shield_hp = 0; self.max_shield = 80
        self.duration = 4.0

    def use(self, player, enemies, projectiles, particles, camera):
        if not self.can_use(): return
        self.shield_hp = self.max_shield
        self.active = True
        self.active_timer = self.duration
        self.timer = self.cooldown
        particles.emit(player.x, player.y, CYAN, 15, speed=
# filename: constants.py
```python
import pygame

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TILE_SIZE = 48

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 50, 220)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 50, 220)
CYAN = (0, 220, 220)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
DARK_RED = (140, 20, 20)
DARK_GREEN = (20, 100, 20)
DARK_BLUE = (20, 20, 100)
BROWN = (139, 90, 43)
GOLD = (255, 200, 0)
PINK = (255, 100, 150)
TEAL = (0, 180, 150)

# Player
PLAYER_SPEED = 220
PLAYER_FRICTION = 0.82
PLAYER_DASH_SPEED = 600
PLAYER_DASH_DURATION = 0.15
PLAYER_DASH_COOLDOWN = 1.2
PLAYER_IFRAME_DURATION = 0.3
PLAYER_HP = 100
PLAYER_MELEE_DAMAGE = 35
PLAYER_MELEE_RANGE = 70
PLAYER_MELEE_COOLDOWN = 0.5

# Weapons
WEAPON_NAMES = [
    "Pistol", "Shotgun", "Railgun", "Grenade Launcher",
    "Chain Lightning", "Boomerang", "Flamethrower", "Sniper"
]

# Enemy tiers
TIER1 = 1
TIER2 = 2
TIER3 = 3

# Layers / Z-order
LAYER_FLOOR = 0
LAYER_HAZARD = 1
LAYER_CRATE = 2
LAYER_ENEMY = 3
LAYER_PLAYER = 4
LAYER_PROJECTILE = 5
LAYER_PARTICLE = 6
LAYER_HUD = 7

# Hazard types
HAZARD_LAVA = "lava"
HAZARD_ICE = "ice"
HAZARD_SPIKES = "spikes"
HAZARD_POISON = "poison"

# Coin values
COIN_SMALL = 1
COIN_MEDIUM = 5
COIN_LARGE = 20