import pygame

# Screen
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "Dungeon Shooter Roguelite"

# Tile
TILE = 48
ARENA_W = 40
ARENA_H = 30

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
LIGHT_GRAY = (200, 200, 200)
DARK_RED = (140, 20, 20)
DARK_BLUE = (20, 40, 140)
GOLD = (255, 200, 50)
PINK = (255, 100, 180)
LIME = (150, 255, 50)
TEAL = (0, 180, 160)
BROWN = (120, 70, 30)
ICE_BLUE = (150, 220, 255)
POISON_GREEN = (80, 200, 80)
LAVA_ORANGE = (255, 100, 20)
DARK_GREEN = (20, 100, 20)

# Player
PLAYER_SPEED = 200
PLAYER_FRICTION = 0.82
PLAYER_MAX_HP = 150
PLAYER_DASH_SPEED = 600
PLAYER_DASH_DURATION = 0.15
PLAYER_DASH_COOLDOWN = 1.2
PLAYER_MELEE_DAMAGE = 40
PLAYER_MELEE_RANGE = 80
PLAYER_MELEE_COOLDOWN = 0.5
PLAYER_IFRAMES = 0.5

# Weapons
WEAPONS = {
    "pistol":      {"name": "Pistol",      "damage": 25,  "fire_rate": 0.25, "ammo": -1,  "color": YELLOW,     "type": "single"},
    "shotgun":     {"name": "Shotgun",     "damage": 15,  "fire_rate": 0.7,  "ammo": 40,  "color": ORANGE,     "type": "pellets"},
    "sniper":      {"name": "Sniper",      "damage": 120, "fire_rate": 1.2,  "ammo": 20,  "color": CYAN,       "type": "pierce"},
    "launcher":    {"name": "Launcher",    "damage": 80,  "fire_rate": 1.5,  "ammo": 15,  "color": RED,        "type": "aoe"},
    "chain":       {"name": "Chain Gun",   "damage": 12,  "fire_rate": 0.08, "ammo": 120, "color": LIGHT_GRAY, "type": "chain"},
    "boomerang":   {"name": "Boomerang",   "damage": 35,  "fire_rate": 0.9,  "ammo": 30,  "color": LIME,       "type": "return"},
    "flamethrower":{"name": "Flamethrower","damage": 8,   "fire_rate": 0.05, "ammo": 80,  "color": LAVA_ORANGE,"type": "cone_dot"},
    "railgun":     {"name": "Railgun",     "damage": 200, "fire_rate": 2.5,  "ammo": 10,  "color": PURPLE,     "type": "rail"},
}

# Secondaries
SECONDARIES = ["shield","grenade","heal","turret","decoy","emp"]

# Enemy tiers
TIER1 = ["goblin","skeleton","bat","slime"]
TIER2 = ["orc","mage","archer","knight"]
TIER3 = ["demon","golem"]

# Wave
BASE_ENEMIES_PER_WAVE = 5
WAVE_SCALE = 3

# Hazards
HAZARD_LAVA    = "lava"
HAZARD_ICE     = "ice"
HAZARD_SPIKES  = "spikes"
HAZARD_POISON  = "poison"

# Layers
LAYER_FLOOR = 0
LAYER_WALL  = 1
LAYER_HAZARD= 2

# Tile types
T_FLOOR   = 0
T_WALL    = 1
T_LAVA    = 2
T_ICE     = 3
T_SPIKES  = 4
T_POISON  = 5
T_CRATE   = 6
T_EMPTY   = 7

# Boss phases
BOSS_PHASE_COUNT = 3