import pygame
import sys
import math
import random
from game import Game

pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Dungeon Shooter Roguelite")
clock = pygame.time.Clock()

def draw_text(surface, text, size, x, y, color=(255,255,255), center=True):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)
    return rect

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(60, 180)
        self.max_life = self.life
        self.color = random.choice([(255,100,0),(255,200,0),(200,50,255),(100,150,255)])
        self.size = random.randint(2,5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = self.life / self.max_life
        r,g,b = self.color
        c = (int(r*alpha), int(g*alpha), int(b*alpha))
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)

class MainMenu:
    def __init__(self):
        self.particles = []
        self.selected = 0
        self.options = ["START RUN", "CONTROLS", "QUIT"]
        self.timer = 0
        self.spawn_timer = 0
        self.show_controls = False
        self.title_bob = 0

    def update(self):
        self.timer += 1
        self.title_bob = math.sin(self.timer * 0.05) * 10
        self.spawn_timer += 1
        if self.spawn_timer >= 3:
            self.spawn_timer = 0
            for _ in range(2):
                x = random.randint(0, SCREEN_W)
                y = random.randint(0, SCREEN_H)
                self.particles.append(Particle(x, y))
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        surface.fill((10, 5, 20))
        # Draw grid
        for x in range(0, SCREEN_W, 60):
            alpha = abs(math.sin(self.timer * 0.02 + x * 0.01))
            c = int(30 * alpha)
            pygame.draw.line(surface, (c, c, c+20), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            alpha = abs(math.sin(self.timer * 0.02 + y * 0.01))
            c = int(30 * alpha)
            pygame.draw.line(surface, (c, c, c+20), (0, y), (SCREEN_W, y))

        for p in self.particles:
            p.draw(surface)

        # Title glow
        title_y = 180 + int(self.title_bob)
        for i in range(3, 0, -1):
            draw_text(surface, "DUNGEON SHOOTER", 80,
                      SCREEN_W//2 + i, title_y + i,
                      (100//i, 20//i, 200//i))
        draw_text(surface, "DUNGEON SHOOTER", 80, SCREEN_W//2, title_y, (220, 100, 255))
        draw_text(surface, "ROGUELITE", 40, SCREEN_W//2, title_y + 70, (150, 200, 255))

        if self.show_controls:
            self._draw_controls(surface)
        else:
            for i, opt in enumerate(self.options):
                col = (255, 220, 0) if i == self.selected else (180, 180, 220)
                scale = 44 if i == self.selected else 36
                y = 350 + i * 70
                if i == self.selected:
                    pulse = abs(math.sin(self.timer * 0.08)) * 30
                    pygame.draw.rect(surface, (int(80+pulse), int(40+pulse//2), int(120+pulse)),
                                     (SCREEN_W//2 - 150, y - 25, 300, 50), border_radius=10)
                draw_text(surface, opt, scale, SCREEN_W//2, y, col)

        draw_text(surface, "Arrow Keys/Mouse to navigate, ENTER to select",
                  18, SCREEN_W//2, SCREEN_H - 30, (100, 100, 150))

    def _draw_controls(self, surface):
        overlay = pygame.Surface((700, 500))
        overlay.set_alpha(220)
        overlay.fill((20, 15, 40))
        surface.blit(overlay, (SCREEN_W//2 - 350, SCREEN_H//2 - 250))
        pygame.draw.rect(surface, (150, 100, 255), (SCREEN_W//2-350, SCREEN_H//2-250, 700, 500), 2, border_radius=8)
        draw_text(surface, "CONTROLS", 36, SCREEN_W//2, SCREEN_H//2 - 220, (220,180,255))
        controls = [
            ("WASD", "Move"),
            ("Mouse", "Aim"),
            ("LMB", "Fire weapon"),
            ("RMB", "Secondary ability"),
            ("SPACE", "Dash (i-frames)"),
            ("E", "Melee attack"),
            ("Q", "Switch weapon"),
            ("1-8", "Select weapon"),
            ("ESC", "Pause / Back"),
        ]
        for idx, (key, desc) in enumerate(controls):
            y = SCREEN_H//2 - 170 + idx * 38
            draw_text(surface, key, 22, SCREEN_W//2 - 120, y, (255, 200, 100))
            draw_text(surface, desc, 22, SCREEN_W//2 + 80, y, (200, 220, 255))
        draw_text(surface, "Press ESC to go back", 20, SCREEN_W//2, SCREEN_H//2 + 230, (150,150,200))

    def handle_event(self, event):
        if self.show_controls:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_controls = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._activate()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._activate()
        return None

    def _activate(self):
        opt = self.options[self.selected]
        if opt == "START RUN":
            return "START"
        elif opt == "CONTROLS":
            self.show_controls = True
        elif opt == "QUIT":
            return "QUIT"
        return None

def main():
    menu = MainMenu()
    state = "MENU"
    game = None

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "MENU":
                result = menu.handle_event(event)
                if result == "START":
                    game = Game(screen, SCREEN_W, SCREEN_H)
                    state = "GAME"
                elif result == "QUIT":
                    pygame.quit()
                    sys.exit()
            elif state == "GAME":
                result = game.handle_event(event)
                if result == "MENU":
                    state = "MENU"
                    menu = MainMenu()
                    game = None
            elif state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        state = "MENU"
                        menu = MainMenu()
                        game = None
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        if state == "MENU":
            menu.update()
            menu.draw(screen)
        elif state == "GAME":
            result = game.update(dt)
            if result == "GAMEOVER":
                state = "GAMEOVER"
            game.draw(screen)
        elif state == "GAMEOVER":
            if game:
                game.draw(screen)
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", 80, SCREEN_W//2, SCREEN_H//2 - 60, (255, 80, 80))
            if game:
                draw_text(screen, f"Score: {game.score}", 40, SCREEN_W//2, SCREEN_H//2 + 20, (255,220,100))
                draw_text(screen, f"Wave: {game.wave}", 30, SCREEN_W//2, SCREEN_H//2 + 70, (200,200,255))
            draw_text(screen, "ENTER to return to menu", 28, SCREEN_W//2, SCREEN_H//2 + 130, (180,180,180))

        pygame.display.flip()

if __name__ == "__main__":
    main()