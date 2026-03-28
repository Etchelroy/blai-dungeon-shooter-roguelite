import pygame
import math
import random
from constants import *
from utils import *
from assets import get_player_surf, get_font
from weapons import WeaponState, fire_weapon
from secondary import make_secondary

class Player:
    def __init__(self, x, y, proj_manager, particles):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 14
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.alive = True

        self.proj_manager = proj_manager
        self.particles = particles

        self.weapon_index = 0
        self.weapons = [WeaponState(i) for i in range(8)]
        self.current_weapon = self.weapons[self.weapon_index]

        self.secondary_index = 0
        self.secondary = make_secondary(SEC_SHIELD)

        self.dash_cooldown = 0.0
        self.dash_timer = 0.0
        self.dashing = False
        self.iframe_timer = 0.0
        self.dash_angle = 0.0
        self.afterimage_timer = 0.0

        self.melee_cooldown = 0.0
        self.melee_active = False
        self.melee_timer = 0.0
        self.melee_angle = 0.0

        self.aim_angle = 0.0
        self.score = 0
        self.coins = 0
        self.combo = 0