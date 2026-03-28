import pygame
import math
import random
from settings import *

class ScreenEffects:
    def __init__(self):
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset = (0, 0)
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.flash_duration = 0
        self.slowmo_factor = 1.0
        self.slowmo_timer = 0
        self.vignette_surf = None
        self.crt_surf = None
        self._build_vignette()
        self._build_crt()
        self.afterimages = []

    def _build_vignette(self):
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        for y in range(0, SCREEN_H, 2):
            for x in range(0, SCREEN_W, 2):
                dx = (x - cx) / cx
                dy = (y - cy) / cy
                dist = math.sqrt(dx * dx + dy * dy)
                alpha = max(0, int((dist - 0.5) * 300))
                alpha = min(200, alpha)
                if alpha > 0:
                    s.set_at((x, y), (0, 0, 0, alpha))
                    if x + 1 < SCREEN_W:
                        s.set_at((x + 1, y), (0, 0, 0, alpha))
                    if y + 1 < SCREEN_H:
                        s.set_at((x, y + 1), (0, 0, 0, alpha))
                    if x + 1 < SCREEN_W and y + 1 < SCREEN_H:
                        s.set_at((x + 1, y + 1), (0, 0, 0, alpha))
        self.vignette_surf = s

    def _build_crt(self):
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 3):
            pygame.draw.line(s, (0, 0, 0, 40), (0, y), (SCREEN_W, y))
        self.crt_surf = s

    def shake(self, intensity=8, duration=0.3):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    def flash(self, color=(255, 255, 255), alpha=180, duration=0.15):
        self.flash_color = color
        self.flash_alpha = max(self.flash_alpha, alpha)
        self.flash_duration = max(self.flash_duration, duration)

    def slowmo(self, factor=0.3, duration=1.5):
        self.slowmo_factor = min(self.slowmo_factor, factor)
        self.slowmo_timer = max(self.slowmo_timer, duration)

    def add_afterimage(self, surface, pos, alpha=120):
        s = surface.copy()
        s.set_alpha(alpha)
        self.afterimages.append({'surf': s, 'pos': pos, 'alpha': alpha, 'timer': 0.2})

    def update(self, dt):
        real_dt = dt
        if self.shake_duration > 0:
            self.shake_duration -= real_dt
            if self.shake_duration <= 0:
                self.shake_intensity = 0
                self.shake_offset = (0, 0)
            else:
                