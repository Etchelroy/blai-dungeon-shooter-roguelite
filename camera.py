import pygame
from constants import SCREEN_W, SCREEN_H
from utils import lerp, clamp

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.shake = 0.0
        self.shake_x = 0
        self.shake_y = 0

    def update(self, target_x, target_y, dt, world_w=0, world_h=0):
        cx = target_x - SCREEN_W // 2
        cy = target_y - SCREEN_H // 2
        if world_w > SCREEN_W:
            cx = clamp(cx, 0, world_w - SCREEN_W)
        else:
            cx = -(SCREEN_W - world_w) // 2
        if world_h > SCREEN_H:
            cy = clamp(cy, 0, world_h - SCREEN_H)
        else:
            cy = -(SCREEN_H - world_h) // 2
        self.x = lerp(self.x, cx, min(1.0, dt * 8))
        self.y = lerp(self.y, cy, min(1.0, dt * 8))
        if self.shake > 0:
            import random
            self.shake_x = random.uniform(-self.shake, self.shake)
            self.shake_y = random.uniform(-self.shake, self.shake)
            self.shake = max(0, self.shake - dt * 80)
        else:
            self.shake_x = 0
            self.shake_y = 0

    def add_shake(self, amount):
        self.shake = min(self.shake + amount, 30)

    def apply(self, x, y):
        return (x - self.x + self.shake_x, y - self.y + self.shake_y)

    def world_pos(self, sx, sy):
        return (sx + self.x - self.shake_x, sy + self.y - self.shake_y)

    def get_offset(self):
        return (int(self.x - self.shake_x), int(self.y - self.shake_y))