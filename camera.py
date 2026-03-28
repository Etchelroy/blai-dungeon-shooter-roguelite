import pygame
import math
import random

class Camera:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = 0
        self.y = 0
        self.shake_intensity = 0
        self.shake_timer = 0

    def follow(self, target_x, target_y):
        self.x = target_x - self.screen_w // 2
        self.y = target_y - self.screen_h // 2

    def shake(self, intensity=8, duration=15):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)

    def update(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            ox = random.randint(-self.shake_intensity, self.shake_intensity)
            oy = random.randint(-self.shake_intensity, self.shake_intensity)
            self.x += ox
            self.y += oy
            if self.shake_timer == 0:
                self.shake_intensity = 0

    def apply(self, x, y):
        return x - self.x, y - self.y

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)