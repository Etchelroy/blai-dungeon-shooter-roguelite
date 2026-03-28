import pygame
import math
import random
from settings import *
from assets import make_bullet_sprite
from utils import normalize, angle_to, vec_from_angle

class Bullet:
    def __init__(self, x, y, vx, vy, damage, wtype, owner='player', pierce=False, aoe=False, aoe_r=0, lifetime=2.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.wtype = wtype
        self.owner = owner
        self.pierce = pierce
        self.aoe = aoe
        self.aoe_r = aoe_r
        self.lifetime = lifetime
        self.alive = True
        self.hit_set = set()
        self.sprite = make_bullet_sprite(wtype)
        self.angle = math.degrees(math.atan2(vy, vx))
        self.chain_count = 0
        self.max_chain = 0
        # Boomerang
        self.returning = False
        self.owner_ref = None
        # Flamethrower DoT
        self.is_dot = False
        self.dot_dmg = 0
        self.dot_dur = 0

    def update(self, dt, arena=None, player=None):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        # Boomerang return
        if self.returning and player:
            tx, ty = player.x, player.y
            dx, dy = normalize(tx-self.x, ty-self.y)
            self.vx = dx*500
            self.vy = dy*500
            if math.hypot(tx-self.x, ty-self.y) < 20:
                self.alive = False
                return
        # Wall collision
        if arena:
            col, row = int(self.x//TILE_PX), int(self.y//TILE_PX)
            if arena.tilemap.is_solid(col, row):
                if self.aoe:
                    self.alive = False
                    return
                if not self.pierce:
                    self.alive = False
                    return
        # Crate collision
        if arena:
            for crate in arena.crates:
                if crate.alive and crate.rect.collidepoint(self.x, self.y):
                    crate.take_damage(self.damage)
                    if not self.pierce:
                        self.alive = False
                    return

    def draw(self, surface, cam_ox, cam_oy):
        if not self.alive: return
        sx = int(self.x - cam_ox)
        sy = int