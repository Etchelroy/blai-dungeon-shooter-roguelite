import pygame
import math
import random
from settings import *

class Particle2D:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(0, SCREEN_H)
        self.vx = random.uniform(-30, 30)
        self.vy = random.uniform(-60, -10)
        self.life = random.uniform(1, 4)
        self.max_life = self.life
        self.size = random.uniform(1, 3)
        self.color = random.choice([(80,80,255),(200,80,255),(80,200,255),(255,120,80)])

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.options = ['START RUN', 'CONTROLS', 'QUIT']
        self.selected = 0
        self.font_title = pygame.font.SysFont('monospace', 64, bold=True)
        self.font_opt = pygame.font.SysFont('monospace', 32, bold=True)
        self.font_small = pygame.font.SysFont('monospace', 14)
        self.t = 0
        self.particles = [Particle2D() for _ in range(60)]
        self.bg_tiles = [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H),
                          random.choice(['+','x','*','#','@'])) for _ in range(40)]

    def update(self, dt):
        self.t += dt
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt
            if p.life <= 0:
                p.reset()
                p.y = SCREEN_H + 10

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mx, my):
                    return self.options[i]
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mx, my):
                    self.selected = i
        return None

    def _option_rects(self):
        rects = []
        sy = SCREEN_H // 2 + 20
        for i in range(len(self.options)):
            rects.append(pygame.Rect(SCREEN_W // 2 - 150, sy + i * 60, 300, 50))
        return rects

    def draw(self, surface):
        surface.fill((5, 5, 20))

        for bx, by, char in self.bg_tiles:
            alpha_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            c = self.font_small.render(char, True, (30, 30, 60, 80))
            alpha_surf.blit(c, (0, 0))
            surface.blit(alpha_surf, (bx, by))

        for p in self.particles:
            a = p.life / p.max_life
            r, g, b = p.color
            col = (int(r * a), int(g * a), int(b * a))
            pygame.draw.circle(surface, col, (int(p.x), int(p.y)), max(1, int(p.size * a)))

        pulse = 0.5 + 0.5 * math.sin(self.t * 2)
        title_col = (
            int(180 + 75 * pulse),
            int(100 + 50 * math.sin(self.t * 1.5)),
            255
        )
        title = self.font_title.render("ROGUE BLASTER", True, title_col)
        glow_surf = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*title_col, 30), glow_surf.get_rect().inflate(20, 10))
        surface.blit(glow_surf, (SCREEN_W // 2 - title.get_width() // 2 - 10, 100 - 5))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 100))

        sub = self.font_small.render("TOP-DOWN ROGUELITE DUNGEON SHOOTER", True, (80, 80, 160))
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 175))

        rects = self._option_rects()
        for i, opt in enumerate(self.options):
            rect = rects[i]
            is_sel = i == self.selected
            if is_sel:
                hover_alpha = int(40 + 30 * math.sin(self.t * 4))
                hs = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                hs.fill((80, 80, 200, hover_alpha))
                surface.blit(hs, rect.topleft)
                pygame.draw.rect(surface, (100, 100, 255), rect, 2, border_radius=4)
                arrow = self.font_opt.render(">", True, (100, 200, 255))
                surface.blit(arrow, (rect.x - 30, rect.y))
            col = (255, 255, 255) if is_sel else (120, 120, 160)
            txt = self.font_opt.render(opt, True, col)
            surface.blit(txt, (rect.x + rect.w // 2 - txt.get_width() // 2,
                                rect.y + rect.h // 2 - txt.get_height() // 2))

        ver = self.font_small.render("v1.0.0  |  WASD+Mouse", True, (40, 40, 60))
        surface.blit(ver, (10, SCREEN_H - 25))


class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.options = ['RESUME', 'CONTROLS', 'QUIT TO MENU']
        self.selected = 0
        self.font_title = pygame.font.SysFont('monospace', 48, bold=True)
        self.font_opt = pygame.font.SysFont('monospace', 28, bold=True)
        self.t = 0

    def update(self, dt):
        self.t += dt

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'RESUME'
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(event.pos):
                    return self.options[i]
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(event.pos):
                    self.selected = i
        return None

    def _option_rects(self):
        rects = []
        sy = SCREEN_H // 2 - 20
        for i in range(len(self.options)):
            rects.append(pygame.Rect(SCREEN_W // 2 - 150, sy + i * 60, 300, 48))
        return rects

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("PAUSED", True, (220, 220, 255))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 180))

        rects = self._option_rects()
        for i, opt in enumerate(self.options):
            rect = rects[i]
            is_sel = i == self.selected
            if is_sel:
                pygame.draw.rect(surface, (60, 60, 160, 100), rect, border_radius=4)
                pygame.draw.rect(surface, (100, 100, 255), rect, 2, border_radius=4)
            col = (255, 255, 255) if is_sel else (120, 120, 160)
            txt = self.font_opt.render(opt, True, col)
            surface.blit(txt, (rect.x + rect.w // 2 - txt.get_width() // 2,
                                rect.y + rect.h // 2 - txt.get_height() // 2))


class ControlsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont('monospace', 36, bold=True)
        self.font = pygame.font.SysFont('monospace', 18)
        self.controls = [
            ("WASD", "Move"),
            ("Mouse", "Aim"),
            ("Left Click / Auto", "Shoot"),
            ("Space", "Dash (i-frames)"),
            ("E", "Melee Attack"),
            ("Q", "Secondary Ability"),
            ("R", "Reload"),
            ("1-8", "Switch Weapon"),
            ("Tab", "Minimap toggle"),
            ("Escape", "Pause"),
            ("Enter", "Confirm"),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                return 'BACK'
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'BACK'
        return None

    def draw(self, surface):
        surface.fill((5, 5, 20))
        title = self.font_title.render("CONTROLS", True, (180, 180, 255))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        pygame.draw