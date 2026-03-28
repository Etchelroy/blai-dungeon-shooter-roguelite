import pygame
import math
import random
from settings import *

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.timer = 0
        self.ox = 0
        self.oy = 0

    def trigger(self, intensity=8, duration=0.3):
        self.intensity = max(self.intensity, intensity)
        self.timer = max(self.timer, duration)

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            self.ox = random.uniform(-self.intensity, self.intensity)
            self.oy = random.uniform(-self.intensity, self.intensity)
            self.intensity *= 0.92
        else:
            self.ox = self.oy = 0
            self.intensity = 0

    def get_offset(self):
        return int(self.ox), int(self.oy)


class FlashEffect:
    def __init__(self):
        self.color = (255,255,255)
        self.alpha = 0
        self.timer = 0
        self.duration = 0.2

    def trigger(self, color=(255,255,255), duration=0.2, alpha=180):
        self.color = color
        self.alpha = alpha
        self.timer = duration
        self.duration = duration
        self._start_alpha = alpha

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            self.alpha = int(self._start_alpha * max(0, self.timer / self.duration))

    def draw(self, surf):
        if self.alpha > 0:
            s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            s.fill((*self.color, self.alpha))
            surf.blit(s, (0, 0))


class SlowMo:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.scale = 1.0
        self.target = 0.2

    def trigger(self, duration=2.0, scale=0.2):
        self.active = True
        self.timer = duration
        self.target = scale

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
                self.scale = 1.0

    def get_scale(self):
        return self.target if self.active else 1.0


class Vignette:
    def __init__(self, w, h):
        self.surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self._build(w, h)
        self.intensity = 0.0

    def _build(self, w, h):
        cx, cy = w//2, h//2
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                dx = (x - cx) / cx
                dy = (y - cy) / cy
                d = min(1.0, math.sqrt(dx*dx + dy*dy))
                a = int(d * d * 200)
                if a > 0:
                    pygame.draw.rect(self.surf, (0,0,0,a), (x,y,4,4))

    def draw(self, surf, intensity=1.0):
        if intensity <= 0:
            return
        s = self.surf.copy()
        s.set_alpha(int(255 * intensity))
        surf.blit(s, (0,0))


class CRTEffect:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.scanline_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(self.scanline_surf, (0,0,0,60), (0,y),(w,y))

    def draw(self, surf):
        surf.blit(self.scanline_surf, (0,0))


class Afterimage:
    def __init__(self):
        self.images = []

    def add(self, surf, x, y, alpha=120):
        img = surf.copy()
        img.set_alpha(alpha)
        self.images.append({'surf': img, 'x': x, 'y': y, 'alpha': alpha, 'timer': 0.25})

    def update(self, dt):
        for im in self.images:
            im['timer'] -= dt
            im['alpha'] = max(0, int(im['alpha'] * 0.85))
            im['surf'].set_alpha(im['alpha'])
        self.images = [im for im in self.images if im['timer'] > 0]

    def draw(self, surf, camera):
        for im in self.images:
            sx, sy = camera.world_to_screen(im['x'], im['y'])
            surf.blit(im['surf'], (sx - im['surf'].get_width()//2, sy - im['surf'].get_height()//2))


class WaveTransition:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.active = False
        self.timer = 0
        self.duration = 1.5
        self.wave_num = 0
        self.phase = 'in'
        self.on_complete = None

    def trigger(self, wave_num, on_complete=None):
        self.active = True
        self.timer = self.duration
        self.wave_num = wave_num
        self.phase = 'in'
        self.on_complete = on_complete

    def update(self, dt):
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= self.duration * 0.5 and self.phase == 'in':
            self.phase = 'out'
            if self.on_complete:
                self.on_complete()
        if self.timer <= 0:
            self.active = False

    def draw(self, surf, font):
        if not self.active:
            return
        progress = self.timer / self.duration
        if self.phase == 'in':
            alpha = int((1 - progress * 2) * 255)
        else:
            alpha = int(progress * 2 * 255)
        alpha = max(0, min(255, alpha))
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill((0,0,0,alpha))
        surf.blit(s, (0,0))
        if alpha > 60:
            txt = font.render(f"WAVE {self.wave_num}", True, (255,255,100))
            txt.set_alpha(alpha)
            surf.blit(txt, (self.w//2 - txt.get_width()//2, self.h//2 - txt.get_height()//2))


class EffectsManager:
    def __init__(self, w, h):
        self.shake = ScreenShake()
        self.flash = FlashEffect()
        self.flash._start_alpha = 0
        self.slowmo = SlowMo()
        self.vignette = Vignette(w, h)
        self.crt = CRTEffect(w, h)
        self.afterimage = Afterimage()
        self.transition = WaveTransition(w, h)
        self.w = w
        self.h = h

    def update(self, dt):
        self.shake.update(dt)
        self.flash.update(dt)
        self.slowmo.update(dt)
        self.afterimage.update(dt)
        self.transition.update(dt)

    def draw_overlays(self, surf, font):
        self.flash.draw(surf)
        self.vignette.draw(surf, 0.4)
        self.crt.draw(surf)
        self.transition.draw(surf, font)