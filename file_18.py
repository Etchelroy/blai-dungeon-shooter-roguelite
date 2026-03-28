import pygame
import math
import random
from settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont('monospace', 72, bold=True)
        self.font_med = pygame.font.SysFont('monospace', 32, bold=True)
        self.font_small = pygame.font.SysFont('monospace', 20)
        self.options = ['START RUN', 'CONTROLS', 'QUIT']
        self.selected = 0
        self.particles = []
        self.time = 0
        self._spawn_bg_particles()

    def _spawn_bg_particles(self):
        for _ in range(60):
            self.particles.append({
                'x': random.randint(0, SCREEN_W),
                'y': random.randint(0, SCREEN_H),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-20, 20),
                'r': random.randint(2, 6),
                'color': random.choice([(255,80,80),(80,80,255),(255,200,60),(80,255,80)]),
                'life': random.uniform(2,6),
                'max_life': 6,
            })

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected].lower().replace(' ', '_')
            elif event.key == pygame.K_ESCAPE:
                return 'quit'
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                oy = 350 + i * 70
                if abs(my - oy) < 25 and abs(mx - SCREEN_W//2) < 150:
                    if self.selected == i:
                        return self.options[i].lower().replace(' ', '_')
                    self.selected = i
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                oy = 350 + i * 70
                if abs(my - oy) < 25 and abs(mx - SCREEN_W//2) < 150:
                    self.selected = i
        return None

    def update(self, dt):
        self.time += dt
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)
                self.particles.append({
                    'x': random.randint(0, SCREEN_W),
                    'y': random.randint(0, SCREEN_H),
                    'vx': random.uniform(-20, 20),
                    'vy': random.uniform(-20, 20),
                    'r': random.randint(2, 6),
                    'color': random.choice([(255,80,80),(80,80,255),(255,200,60),(80,255,80)]),
                    'life': random.uniform(3,7),
                    'max_life': 7,
                })

    def draw(self):
        self.screen.fill((8, 8, 20))
        for p in self.particles:
            alpha = int(200 * (p['life'] / p['max_life']))
            s = pygame.Surface((p['r']*2, p['r']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (p['r'], p['r']), p['r'])
            self.screen.blit(s, (int(p['x']-p['r']), int(p['y']-p['r'])))

        pulse = 0.05 * math.sin(self.time * 3)
        title_color = (
            int(200 + 55 * math.sin(self.time * 2)),
            int(100 + 50 * math.sin(self.time * 1.5)),
            int(255),
        )
        title = self.font_big.render("DUNGEON BLASTER", True, title_color)
        scale = 1.0 + pulse
        scaled = pygame.transform.scale(title, (int(title.get_width()*scale), int(title.get_height()*scale)))
        self.screen.blit(scaled, (SCREEN_W//2 - scaled.get_width()//2, 120))

        sub = self.font_small.render("A Roguelite Dungeon Shooter", True, (150, 150, 200))
        self.screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 220))

        for i, opt in enumerate(self.options):
            selected = i == self.selected
            ox = SCREEN_W//2
            oy = 350 + i * 70
            if selected:
                bw = 300 + int(10 * math.sin(self.time * 4))
                pygame.draw.rect(self.screen, (40, 40, 80), (ox - bw//2, oy - 28, bw, 56), border_radius=8)
                pygame.draw.rect(self.screen, (100, 100, 255), (ox - bw//2, oy - 28, bw, 56), 2, border_radius=8)
                color = (255, 255, 100)
                arr = self.font_med.render(">", True, (255,200,60))
                self.screen.blit(arr, (ox - 170, oy - arr.get_height()//2))
            else:
                color = (160, 160, 200)
            t = self.font_med.render(opt, True, color)
            self.screen.blit(t, (ox - t.get_width()//2, oy - t.get_height()//2))

        hint = self.font_small.render("UP/DOWN to navigate  ENTER to select", True, (80,80,120))
        self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 40))
        pygame.display.flip()


class ControlsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('monospace', 28, bold=True)
        self.font_s = pygame.font.SysFont('monospace', 20)
        self.controls = [
            ("WASD", "Move"),
            ("Mouse", "Aim"),
            ("Left Click", "Fire weapon"),
            ("Right Click", "Secondary ability"),
            ("SPACE", "Dash (i-frames + afterimage)"),
            ("E", "Melee attack"),
            ("Q", "Switch weapon"),
            ("1-6", "Select ability"),
            ("ESC", "Pause"),
            ("R (pause)", "Restart"),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            return 'back'
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'back'
        return None

    def draw(self):
        self.screen.fill((8, 8, 20))
        t = self.font.render("CONTROLS", True, (255, 220, 60))
        self.screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 40))
        pygame.draw.line(self.screen, (80,80,120), (100, 90), (SCREEN_W-100, 90), 2)
        for i, (key, action) in enumerate(self.controls):
            y = 120 + i * 48
            ks = self.font_s.render(key, True, (100, 200, 255))
            as_ = self.font_s.render(action, True, (200, 200, 200))
            self.screen.blit(ks, (150, y))
            self.screen.blit(as_, (420, y))
            pygame.draw.line(self.screen, (30,30,60), (150, y+36), (SCREEN_W-150, y+36), 1)
        back = self.font_s.render("Press any key to return", True, (80,80,120))
        self.screen.blit(back, (SCREEN_W//2 - back.get_width()//2, SCREEN_H - 50))
        pygame.display.flip()


class DeathScreen:
    def __init__(self, screen, game):
        self.screen = screen
        self.font_big = pygame.font.SysFont('monospace', 64, bold=True)
        self.font_med = pygame.font.SysFont('monospace', 28, bold=True)
        self.font_s = pygame.font.SysFont('monospace', 20)
        self.game = game
        self.time = 0
        self.typewriter_idx = 0
        self.typewriter_timer = 0
        self.lines = [
            f"Wave Reached: {game.wave}",
            f"Score: {game.score}",
            f"Coins Collected: {game.coins}",
            f"Enemies Slain: {game.enemy_manager.total_killed}",
            f"Bosses Slain: {game.boss_manager.total_killed}",
            f"Time Survived: {int(game.game_time)}s",
        ]
        self.displayed_lines = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return 'restart'
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                return 'menu'
        return None

    def update(self, dt):
        self.time += dt
        self.typewriter_timer += dt
        if self.typewriter_timer >= 0.08 and self.typewriter_idx < len(self.lines):
            self.displayed_lines = self.lines[:self.typewriter_idx+1]
            self.typewriter_idx += 1
            self.typewriter_timer = 0

    def draw(self):
        self.screen.fill((5, 2, 10))
        pulse = abs(math.sin(self.time * 2))
        r = int(180 + 75 * pulse)
        t = self.font_big.render("YOU DIED", True, (r, 30, 30))
        self.screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 80))

        y = 200
        for line in self.displayed_lines:
            s = self.font_med.render(line, True, (200, 200, 255))
            self.screen.blit(s, (SCREEN_W//2 - s.get_width()//2, y))
            y += 50

        if self.typewriter_idx >= len(self.lines):
            r_hint = self.font_s.render("[R] Restart    [Q] Main Menu", True, (120,120,180))
            self.screen.blit(r_hint, (SCREEN_W//2 - r_hint.get_width()//2, SCREEN_H - 60))

        pygame.display.flip()