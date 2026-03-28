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