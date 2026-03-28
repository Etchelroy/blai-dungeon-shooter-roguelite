import pygame
import math
import sys
from constants import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('impact', 72)
        self.font_item = pygame.font.SysFont('arial', 36, bold=True)
        self.font_sm = pygame.font.SysFont('arial', 20)
        self.options = ['START RUN', 'CONTROLS', 'QUIT']
        self.selected = 0
        self.state = 'main'  # 'main' or 'controls'
        self.particles = []
        self.timer = 0.0
        self.bg_particles = []
        for _ in range(60):
            self.bg_particles.append({
                'x': random.uniform(0, SCREEN_W),
                'y': random.uniform(0, SCREEN_H),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-60, -10),
                'life': random.uniform(0, 3),
                'max_life': random.uniform(2, 5),
                'r': random.randint(1, 3),
                'color': random.choice([(255,80,0),(255,150,0),(200,50,200),(80,150,255)])
            })

    def handle_event(self, event):
        if self.state == 'controls':
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                self.state = 'main'
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                oy = SCREEN_H // 2 + 20 + i * 70
                ox = SCREEN_W // 2
                if abs(mx - ox) < 150 and abs(my - oy) < 25:
                    self.selected = i
                    return self._activate()
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                oy = SCREEN_H // 2 + 20 + i * 70
                if abs(mx - SCREEN_W//2) < 150 and abs(my - oy) < 25:
                    self.selected = i
        return None

    def _activate(self):
        opt = self.options[self.selected]
        if opt == 'START RUN':
            return 'start'
        elif opt == 'CONTROLS':
            self.state = 'controls'
            return None
        elif opt == 'QUIT':
            pygame.quit()
            sys.exit()

    def update(self, dt):
        self.timer += dt
        for p in self.bg_particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] += dt
            if p['life'] >= p['max_life'] or p['y'] < -10 or p['x'] < -10 or p['x'] > SCREEN_W + 10:
                p['x'] = random.uniform(0, SCREEN_W)
                p['y'] = random.uniform(SCREEN_H, SCREEN_H + 50)
                p['vx'] = random.uniform(-30, 30)
                p['vy'] = random.uniform(-80, -20)
                p['life'] = 0
                p['max_life'] = random.uniform(2, 5)

    def draw(self):
        self.screen.fill((8, 5, 15))

        # Animated bg particles
        for p in self.bg_particles:
            alpha = 1.0 - p['life'] / p['max_life']
            r, g, b = p['color']
            c = (int(r * alpha), int(g * alpha), int(b * alpha))
            pygame.draw.circle(self.screen, c, (int(p['x']), int(p['y'])), p['r'])

        # Title
        title_wave = math.sin(self.timer * 2) * 8
        title_surf = self.font_title.render('DUNGEON SHOOTER', True, (255, 80, 0))
        title_shadow = self.font_title.render('DUNGEON SHOOTER', True, (120, 30, 0))
        tx = SCREEN_W // 2 - title_surf.get_width() // 2
        ty = int(SCREEN_H // 4 + title_wave)
        self.screen.blit(title_shadow, (tx + 4, ty + 4))
        self.screen.blit(title_surf, (tx, ty))

        sub_surf = self.font_sm.render('ROGUELITE', True, (200, 150, 255))
        self.screen.blit(sub_surf, (SCREEN_W//2 - sub_surf.get_width()//2, ty + 80))

        if self.state == 'controls':
            self._draw_controls()
        else:
            self._draw_menu()

    def _draw_menu(self):
        for i, opt in enumerate(self.options):
            oy = SCREEN_H // 2 + 20 + i * 70
            ox = SCREEN_W // 2
            is_sel = (i == self.selected)
            scale = 1.0 + 0.08 * math.sin(self.timer * 4) if is_sel else 1.0
            color = (255, 220, 50) if is_sel else (180, 180, 200)
            txt = self.font_item.render(opt, True, color)
            if is_sel:
                glow_surf = self.font_item.render(opt, True, (255, 100, 0))
                glow_surf.set_alpha(80)
                self.screen.blit(glow_surf, (ox - txt.get_width()//2 - 2, oy - txt.get_height()//2 - 2))
                arrow = self.font_item.render('>', True, (255, 200, 0))
                self.screen.blit(arrow, (ox - txt.get_width()//2 - 40, oy - txt.get_height()//2))
            self.screen.blit(txt, (ox - txt.get_width()//2, oy - txt.get_height()//2))

        hint = self.font_sm.render('Arrow keys / Mouse to navigate, Enter to select', True, (100,100,120))
        self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 40))

    def _draw_controls(self):
        lines = [
            'CONTROLS',
            '',
            'WASD         - Move',
            'Mouse        - Aim',
            'LMB / Auto   - Shoot',
            'SPACE        - Dash (i-frames)',
            'E            - Melee attack',
            'R            - Reload',
            'Q            - Secondary ability',
            '1-8          - Switch weapon',
            '',
            'Press ENTER or ESC to go back',
        ]
        y = SCREEN_H // 3
        for line in lines:
            color = (255, 200, 50) if line == 'CONTROLS' else (200, 200, 220)
            fnt = self.font_item if line == 'CONTROLS' else self.font_sm
            surf = fnt.render(line, True, color)
            self.screen.blit(surf, (SCREEN_W//2 - surf.get_width()//2, y))
            y += surf.get_height() + 6

import random