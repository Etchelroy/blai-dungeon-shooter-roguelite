import pygame
import random
import math

from player import Player
from enemies import (Grunt, Brute, Speeder, Sniper, Shielder,
                     Exploder, Summoner, Phantom, TankEnemy, BerserkerEnemy)
from bosses import Boss1, Boss2, Boss3
from arena import Arena
from hud import HUD
from particles import ParticleSystem
from camera import Camera
from weapons import (Pistol, Shotgun, RailGun, RocketLauncher,
                     ChainLightning, BoomerangGun, FlameThrower, GrenadeLauncher)
from abilities import (ShieldBubble, TimeSlow, TurretDeploy,
                       BlackHole, MineLayer, AdrenalineRush)

SCREEN_W, SCREEN_H = 1280, 720
ARENA_W, ARENA_H = 3200, 3200

ENEMY_TIERS = [
    [Grunt, Speeder, Sniper],
    [Brute, Shielder, Exploder, Summoner],
    [Phantom, TankEnemy, BerserkerEnemy],
]

BOSS_CLASSES = [Boss1, Boss2, Boss3]

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "playing"

        self.arena = Arena(ARENA_W, ARENA_H)
        self.particles = ParticleSystem()
        self.camera = Camera(SCREEN_W, SCREEN_H)
        self.hud = HUD(SCREEN_W, SCREEN_H)

        spawn = self.arena.get_spawn_point()
        self.player = Player(spawn[0], spawn[1], self.particles)
        self.player.arena_w = ARENA_W
        self.player.arena_h = ARENA_H

        self._give_starting_weapons()
        self._give_starting_secondary()

        self.enemies = []
        self.boss = None
        self.projectiles = []
        self.wave = 0
        self.score = 0
        self.coins = 0
        self.wave_timer = 0.0
        self.wave_delay = 2.0
        self.wave_active = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0.0
        self.boss_wave_interval = 5

        self.game_over = False
        self.victory = False
        self.game_over_timer = 0.0

        self.font = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 24)

        self._start_next_wave()

    def _give_starting_weapons(self):
        weapons = [
            Pistol(), Shotgun(), RailGun(), RocketLauncher(),
            ChainLightning(), BoomerangGun(), FlameThrower(), GrenadeLauncher()
        ]
        self.player.weapons = weapons
        self.player.weapon_index = 0

    def _give_starting_secondary(self):
        secondaries = [
            ShieldBubble(), TimeSlow(), TurretDeploy(),
            BlackHole(), MineLayer(), AdrenalineRush()
        ]
        self.player.secondary = secondaries[0]
        self.player.secondaries = secondaries
        self.player.secondary_index = 0

    def _start_next_wave(self):
        self.wave += 1
        self.wave_active = True

        if self.wave % self.boss_wave_interval == 0:
            boss_idx = (self.wave // self.boss_wave_interval - 1) % len(BOSS_CLASSES)
            spawn = self.arena.get_spawn_point()
            self.boss = BOSS_CLASSES[boss_idx](spawn[0], spawn[1], self.particles)
            self.enemies_to_spawn = []
        else:
            self.boss = None
            count = min(5 + self.wave * 3, 40)
            tier = min(2, (self.wave - 1) // 3)
            pool = []
            for t in range(tier + 1):
                pool.extend(ENEMY_TIERS[t])
            self.enemies_to_spawn = [random.choice(pool) for _ in range(count)]
            self.spawn_timer = 0.0

    def _spawn_enemy(self, cls):
        margin = 200
        while True:
            x = random.uniform(margin, ARENA_W - margin)
            y = random.uniform(margin, ARENA_H - margin)
            dx = x - self.player.x
            dy = y - self.player.y
            if math.sqrt(dx*dx + dy*dy) > 300:
                break
        e = cls(x, y, self.particles)
        e.arena_w = ARENA_W
        e.arena_h = ARENA_H
        self.enemies.append(e)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            self._handle_events()
            if not self.game_over:
                self._update(dt)
            else:
                self.game_over_timer -= dt
                if self.game_over_timer <= 0:
                    self.running = False
            self._draw()
        return "menu" if self.game_over else "menu"

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    if self.player.weapons:
                        self.player.weapon_index = (self.player.weapon_index + 1) % len(self.player.weapons)
                elif event.key == pygame.K_q:
                    if self.player.secondary:
                        self.player.secondary.activate(self.player, self.enemies, self.particles)
                elif event.key == pygame.K_r:
                    w = self._current_weapon()
                    if w and hasattr(w, 'start_reload'):
                        w.start_reload()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                    idx = event.key - pygame.K_1
                    if idx < len(self.player.weapons):
                        self.player.weapon_index = idx
                elif event.key == pygame.K_F1:
                    idx = (self.player.secondary_index + 1) % len(self.player.secondaries)
                    self.player.secondary_index = idx
                    self.player.secondary = self.player.secondaries[idx]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._player_shoot()
            self.player.handle_event(event)

    def _current_weapon(self):
        if self.player.weapons:
            return self.player.weapons[self.player.weapon_index]
        return None

    def _player_shoot(self):
        w = self._current_weapon()
        if w is None:
            return
        mx, my = pygame.mouse.get_pos()
        wx = mx + self.camera.offset_x
        wy = my + self.camera.offset_y
        new_projs = w.fire(self.player.x, self.player.y, wx, wy, self.player)
        if new_projs:
            self.projectiles.extend(new_projs)

    def _update(self, dt):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        wx = mx + self.camera.offset_x
        wy = my + self.camera.offset_y

        # Continuous fire for auto weapons
        if pygame.mouse.get_pressed()[0]:
            w = self._current_weapon()
            if w and getattr(w, 'auto', False):
                new_projs = w.fire(self.player.x, self.player.y, wx, wy, self.player)
                if new_projs:
                    self.projectiles.extend(new_projs)

        self.player.update(dt, keys, wx, wy, self.arena)
        self.player.enemies_ref = self.enemies

        # Melee
        melee_projs = self.player.get_melee_projectiles()
        self.projectiles.extend(melee_projs)

        # Secondary update
        if self.player.secondary:
            result = self.player.secondary.update(dt, self.player, self.enemies, self.particles)
            if result:
                self.projectiles.extend(result)

        # Turret projectiles
        if hasattr(self.player, 'turrets'):
            for turret in self.player.turrets:
                turret.update(dt, self.enemies)
                self.projectiles.extend(turret.get_projectiles())

        # Spawn wave enemies
        if self.enemies_to
Looking at what's been built across shifts, I need to complete the remaining systems and ensure everything integrates properly. Let me assess what's needed:

- `hud.py` - Full HUD rendering
- `menu.py` - Animated main menu
- `game.py` - Game loop with wave/boss logic
- `main.py` - Entry point (may need updates)
- Verification that all systems connect

```python
# filename: menu.py
import pygame
import math
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.5, 2.0)
        self.max_life = self.life
        self.color = random.choice([
            (255, 100, 50), (255, 200, 50), (200, 50, 255),
            (50, 200, 255), (255, 50, 100)
        ])
        self.size = random.uniform(2, 5)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.02
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        alpha = max(0, self.life / self.max_life)
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, (r, g, b), (int(self.x), int(self.y)), size)


class MenuOption:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.scale = 1.0
        self.target_scale = 1.0
        self.color = (220, 220, 220)
        self.target_color = (220, 220, 220)
        self.glow = 0.0

    def update(self, dt, hovered):
        if hovered:
            self.target_scale = 1.15
            self.target_color = (255, 220, 50)
            self.glow = min(1.0, self.glow + dt * 4)
        else:
            self.target_scale = 1.0
            self.target_color = (220, 220, 220)
            self.glow = max(0.0, self.glow - dt * 4)
        self.scale += (self.target_scale - self.scale) * min(1, dt * 8)
        cr = int(self.color[0] + (self.target_color[0] - self.color[0]) * min(1, dt * 8))
        cg = int(self.color[1] + (self.target_color[1] - self.color[1]) * min(1, dt * 8))
        cb = int(self.color[2] + (self.target_color[2] - self.color[2]) * min(1, dt * 8))
        self.color = (cr, cg, cb)

    def draw(self, surf, font):
        if self.glow > 0:
            glow_surf = font.render(self.text, True, (255, 180, 0))
            gw = int(glow_surf.get_width() * self.scale)
            gh = int(glow_surf.get_height() * self.scale)
            if gw > 0 and gh > 0:
                glow_surf = pygame.transform.scale(glow_surf, (gw, gh))
                for offset in range(3, 0, -1):
                    alpha = int(80 * self.glow / offset)
                    glow_surf.set_alpha(alpha)
                    surf.blit(glow_surf, (self.x - gw // 2 - offset, self.y - gh // 2 - offset))

        text_surf = font.render(self.text, True, self.color)
        tw = int(text_surf.get_width() * self.scale)
        th = int(text_surf.get_height() * self.scale)
        if tw > 0 and th > 0:
            text_surf = pygame.transform.scale(text_surf, (tw, th))
            surf.blit(text_surf, (self.x - tw // 2, self.y - th // 2))

    def get_rect(self, font):
        text_surf = font.render(self.text, True, self.color)
        tw = int(text_surf.get_width() * self.scale)
        th = int(text_surf.get_height() * self.scale)
        return pygame.Rect(self.x - tw // 2, self.y - th // 2, tw, th)


class ControlsScreen:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.alpha = 0
        self.fade_in = True
        self.controls = [
            ("MOVEMENT", "WASD - Move with momentum/friction"),
            ("AIM", "Mouse - Aim direction"),
            ("SHOOT", "Left Click / Auto - Fire weapon"),
            ("DASH", "Spacebar - Dash with i-frames + afterimage"),
            ("MELEE", "E - Melee attack"),
            ("ABILITY", "Right Click - Secondary ability"),
            ("WEAPON 1-8", "1-8 Keys - Switch weapons"),
            ("PAUSE", "ESC - Pause game"),
            ("", ""),
            ("WEAPONS", ""),
            ("Pistol", "Fast, accurate single shots"),
            ("Shotgun", "8 pellets, spread fire"),
            ("Sniper", "Pierce through enemies"),
            ("Rocket", "AoE explosion"),
            ("Chain Gun", "Rapid chain lightning"),
            ("Boomerang", "Returns to player"),
            ("Flamethrower", "Cone DoT fire"),
            ("Grenade", "Bouncing AoE launcher"),
        ]

    def update(self, dt):
        if self.fade_in:
            self.alpha = min(255, self.alpha + int(dt * 500))

    def draw(self, surf):
        overlay = pygame.Surface((self.screen_w, self.screen_h))
        overlay.fill((10, 5, 20))
        overlay.set_alpha(self.alpha)
        surf.blit(overlay, (0, 0))

        if self.alpha < 50:
            return

        try:
            title_font = pygame.font.Font(None, 52)
            font = pygame.font.Font(None, 28)
            small_font = pygame.font.Font(None, 22)
        except Exception:
            title_font = pygame.font.SysFont('arial', 40)
            font = pygame.font.SysFont('arial', 22)
            small_font = pygame.font.SysFont('arial', 18)

        title = title_font.render("CONTROLS", True, (255, 180, 50))
        surf.blit(title, (self.screen_w // 2 - title.get_width() // 2, 40))

        back_text = small_font.render("Press ESC or BACKSPACE to return", True, (150, 150, 150))
        surf.blit(back_text, (self.screen_w // 2 - back_text.get_width() // 2, self.screen_h - 40))

        col1_x = self.screen_w // 4
        col2_x = 3 * self.screen_w // 4
        start_y = 110
        line_h = 28

        for i, (key, desc) in enumerate(self.controls):
            if i >= 9:
                x = col2_x
                row = i - 9
            else:
                x = col1_x
                row = i

            y = start_y + row * line_h

            if key and not desc:
                t = title_font.render(key, True, (200, 100, 255))
                surf.blit(t, (x - t.get_width() // 2, y))
            elif key:
                kt = font.render(key, True, (255, 200, 50))
                dt_surf = font.render(desc, True, (200, 200, 200))
                surf.blit(kt, (x - 180, y))
                surf.blit(dt_surf, (x - 60, y))
            else:
                pass


class MainMenu:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.particles = []
        self.spawn_timer = 0.0
        self.time = 0.0
        self.state = "menu"  # "menu", "controls", "fadeout"
        self.fade_alpha = 0
        self.fade_out = False
        self.result = None  # "start", "quit"
        self.controls_screen = ControlsScreen(screen_w, screen_h)

        cy = screen_h // 2
        self.options = [
            MenuOption("START RUN", screen_w // 2, cy - 20),
            MenuOption("CONTROLS", screen_w // 2, cy + 60),
            MenuOption("QUIT", screen_w // 2, cy + 140),
        ]
        self.option_names = ["start", "controls", "quit"]

        try:
            self.title_font = pygame.font.Font(None, 96)
            self.sub_font = pygame.font.Font(None, 36)
            self.option_font = pygame.font.Font(None, 52)
        except Exception:
            self.title_font = pygame.font.SysFont('arial', 72)
            self.sub_font = pygame.font.SysFont('arial', 28)
            self.option_font = pygame.font.SysFont('arial', 40)

        self.title_alpha = 0
        self.title_offset = -60
        self.intro_timer = 0.0

        self.bg_stars = [(random.randint(0, screen_w), random.randint(0, screen_h),
                          random.uniform(0.3, 1.5)) for _ in range(120)]

        self.scanline_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        for y in range(0, screen_h, 4):
            pygame.draw.line(self.scanline_surf, (0, 0, 0, 30), (0, y), (screen_w, y))

    def update(self, dt):
        self.time += dt
        self.intro_timer += dt

        if self.intro_timer < 1.0:
            self.title_alpha = min(255, int(self.intro_timer * 300))
            self.title_offset = int(-60 * (1.0 - self.intro_timer))
        else:
            self.title_alpha = 255
            self.title_offset = 0

        self.spawn_timer += dt
        if self.spawn_timer > 0.05:
            self.spawn_timer = 0
            if len(self.particles) < 200:
                x = random.randint(0, self.screen_w)
                y = random.randint(0, self.screen_h)
                self.particles.append(Particle(x, y))

        self.particles = [p for p in self.particles if p.update(dt)]

        if self.state == "controls":
            self.controls_screen.update(dt)
            return

        if self.fade_out:
            self.fade_alpha = min(255, self.fade_alpha + int(dt * 400))
            if self.fade_alpha >= 255:
                pass
            return

        mx, my = pygame.mouse.get_pos()
        for i, opt in enumerate(self.options):
            rect = opt.get_rect(self.option_font)
            hovered = rect.collidepoint(mx, my)
            opt.update(dt, hovered)

    def handle_event(self, event):
        if self.state == "controls":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.state = "menu"
                self.controls_screen.alpha = 0
                self.controls_screen.fade_in = True
            return None

        if self.fade_out:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for i, opt in enumerate(self.options):
                rect = opt.get_rect(self.option_font)
                if rect.collidepoint(mx, my):
                    name = self.option_names[i]
                    if name == "controls":
                        self.state = "controls"
                        self.controls_screen.alpha = 0
                        return None
                    elif name == "quit":
                        return "quit"
                    elif name == "start":
                        self.fade_out = True
                        self.result = "start"
                        return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.fade_out = True
                self.result = "start"
            elif event.key == pygame.K_ESCAPE:
                return "quit"

        return None

    def is_done(self):
        return self.fade_out and self.fade_alpha >= 255

    def draw(self, surf):
        surf.fill((8, 5, 18))

        for (sx, sy, brightness) in self.bg_stars:
            twinkle = 0.5 + 0.5 * math.sin(self.time * 2 + sx * 0.1)
            c = int(brightness * twinkle * 180)
            c = max(0, min(255, c))
            pygame.draw.circle(surf, (c, c, c), (int(sx), int(sy)), 1)

        for p in self.particles:
            p.draw(surf)

        surf.blit(self.scanline_surf, (0, 0))

        wave_x = math.sin(self.time * 0.8) * 8
        wave_y = math.cos(self.time * 0.6) * 4

        if self.title_alpha > 0:
            title1 = self.title_font.render("DUNGEON", True, (255, 80, 30))
            title2 = self.title_font.render("SHOOTER", True, (200, 50, 255))

            title1.set_alpha(self.title_alpha)
            title2.set_alpha(self.title_alpha)

            tx1 = self.screen_w // 2 - title1.get_width() // 2 + int(wave_x)
            ty1 = 80 + self.title_offset + int(wave_y)
            tx2 = self.screen_w // 2 - title2.get_width() // 2 - int(wave_x)
            ty2 = 160 + self.title_offset - int(wave_y)

            glow1 = self.title_font.render("DUNGEON", True, (100, 30, 10))
            glow1.set_alpha(int(self.title_alpha * 0.4))
            surf.blit(glow1, (tx1 + 3, ty1 + 3))
            surf.blit(title1, (tx1, ty1))

            glow2 = self.title_font.render("SHOOTER", True, (80, 20, 100))
            glow2.set_alpha(int(self.title_alpha * 0.4))
            surf.blit(glow2, (tx2 + 3, ty2 + 3))
            surf.blit(title2, (tx2, ty2))

            sub = self.sub_font.render("ROGUELITE", True, (150, 150, 200))
            sub.set_alpha(self.title_alpha)
            surf.blit(sub, (self.screen_w // 2 - sub.get_width() // 2, ty2 + 70))

        if self.state == "menu" and not self.fade_out:
            for opt in self.options:
                opt.draw(surf, self.option_font)

        if self.state == "controls":
            self.controls_screen.draw(surf)

        if self.fade_out and self.fade_alpha > 0:
            fade_surf = pygame.Surface((self.screen_w, self.screen_h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            surf.blit(fade_surf, (0, 0))