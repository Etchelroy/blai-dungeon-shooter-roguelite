import pygame
import math
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.3, 1.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(1.5, 4.0)
        self.max_life = self.life
        self.size = random.randint(2, 5)
        self.color = random.choice([
            (255, 80, 80), (80, 80, 255), (255, 200, 0),
            (0, 255, 180), (200, 0, 255)
        ])

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        r, g, b = self.color
        c = (int(r * alpha), int(g * alpha), int(b * alpha))
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.sw, self.sh = screen.get_size()
        self.options = ["START RUN", "CONTROLS", "QUIT"]
        self.selected = 0
        self.font_title = pygame.font.SysFont('Arial', 72, bold=True)
        self.font_option = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.time = 0.0
        self.particles = []
        self.spawn_timer = 0.0
        self.state = "main"  # main or controls
        self.bg_surface = pygame.Surface((self.sw, self.sh))
        self._make_bg()
        self.title_y = self.sh * 0.22
        self.option_start_y = self.sh * 0.48

    def _make_bg(self):
        for y in range(self.sh):
            ratio = y / self.sh
            r = int(5 + ratio * 15)
            g = int(0 + ratio * 5)
            b = int(20 + ratio * 30)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (self.sw, y))

    def handle_event(self, event):
        if self.state == "controls":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.state = "main"
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for i, opt in enumerate(self.options):
                oy = self.option_start_y + i * 70
                rect = pygame.Rect(self.sw // 2 - 150, oy - 25, 300, 50)
                if rect.collidepoint(mx, my):
                    self.selected = i
                    return self._activate()
        elif event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            for i, opt in enumerate(self.options):
                oy = self.option_start_y + i * 70
                rect = pygame.Rect(self.sw // 2 - 150, oy - 25, 300, 50)
                if rect.collidepoint(mx, my):
                    self.selected = i
        return None

    def _activate(self):
        opt = self.options[self.selected]
        if opt == "START RUN":
            return "start"
        elif opt == "CONTROLS":
            self.state = "controls"
            return None
        elif opt == "QUIT":
            return "quit"
        return None

    def update(self, dt):
        self.time += dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = 0.05
            x = random.uniform(0, self.sw)
            y = random.uniform(0, self.sh)
            self.particles.append(Particle(x, y))

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        if len(self.particles) > 200:
            self.particles = self.particles[-200:]

    def draw(self):
        self.screen.blit(self.bg_surface, (0, 0))

        for p in self.particles:
            p.draw(self.screen)

        if self.state == "controls":
            self._draw_controls()
            return

        # Animated title
        wave = math.sin(self.time * 2) * 8
        title_text = "DUNGEON SLAYER"
        colors = [(255, 80, 80), (255, 150, 50), (255, 220, 80), (80, 255, 150), (80, 150, 255)]
        for i, ch in enumerate(title_text):
            char_wave = math.sin(self.time * 3 + i * 0.5) * 6
            cf = colors[i % len(colors)]
            cs = self.font_title.render(ch, True, cf)
            total_w = self.font_title.size(title_text)[0]
            cx = self.sw // 2 - total_w // 2 + self.font_title.size(title_text[:i])[0]
            self.screen.blit(cs, (cx, self.title_y + char_wave))

        subtitle = self.font_small.render("A Roguelite Dungeon Shooter", True, (150, 150, 200))
        self.screen.blit(subtitle, (self.sw // 2 - subtitle.get_width() // 2, self.title_y + 85))

        for i, opt in enumerate(self.options):
            oy = self.option_start_y + i * 70
            is_sel = (i == self.selected)
            if is_sel:
                pulse = abs(math.sin(self.time * 4)) * 0.4 + 0.6
                glow_r = pygame.Surface((320, 60), pygame.SRCALPHA)
                glow_r.fill((255, 200, 50, int(40 * pulse)))
                self.screen.blit(glow_r, (self.sw // 2 - 160, oy - 30))

                box_color = (
                    int(180 + 75 * pulse),
                    int(100 + 100 * pulse),
                    int(0 + 50 * pulse)
                )
                pygame.draw.rect(self.screen, box_color,
                                 (self.sw // 2 - 155, oy - 28, 310, 56), 3, border_radius=8)
                text_color = (255, 255, 100)
            else:
                text_color = (160, 160, 200)

            shadow = self.font_option.render(opt, True, (0, 0, 0))
            self.screen.blit(shadow, (self.sw // 2 - shadow.get_width() // 2 + 2, oy - 18 + 2))
            txt = self.font_option.render(opt, True, text_color)
            self.screen.blit(txt, (self.sw // 2 - txt.get_width() // 2, oy - 18))

        hint = self.font_small.render("Arrow keys/Mouse to navigate  |  Enter/Click to select", True, (80, 80, 120))
        self.screen.blit(hint, (self.sw // 2 - hint.get_width() // 2, self.sh - 40))

    def _draw_controls(self):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_option.render("CONTROLS", True, (255, 200, 50))
        self.screen.blit(title, (self.sw // 2 - title.get_width() // 2, 80))

        controls = [
            ("WASD", "Move with momentum"),
            ("Mouse", "Aim"),
            ("Left Click", "Fire weapon"),
            ("E", "Melee attack"),
            ("Space", "Dash (i-frames + afterimage)"),
            ("Q", "Secondary ability"),
            ("R", "Reload"),
            ("1-8", "Switch weapons"),
            ("Tab", "Cycle weapons"),
        ]
        y = 160
        for key, desc in controls:
            ks = self.font_small.render(key, True, (255, 200, 100))
            ds = self.font_small.render(desc, True, (200, 200, 220))
            self.screen.blit(ks, (self.sw // 2 - 220, y))
            self.screen.blit(ds, (self.sw // 2 - 60, y))
            y += 32

        back = self.font_small.render("Press any key to go back", True, (120, 120, 160))
        self.screen.blit(back, (self.sw // 2 - back.get_width() // 2, self.sh - 60))