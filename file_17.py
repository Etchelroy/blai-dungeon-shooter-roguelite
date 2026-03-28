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
                
# filename: game.py
```python
import pygame
import sys
import math
import random
from settings import *
from utils import *
from assets import Assets
from camera import Camera
from lighting import LightingSystem
from tilemap import TileMap
from arena import Arena
from spatial_hash import SpatialHash
from particles import ParticleSystem
from effects import EffectsManager
from player import Player
from enemies import EnemyManager
from bosses import BossManager
from hud import HUD
from shop import Shop
from upgrades import UpgradeSystem
from weapons import WeaponManager
from abilities import AbilityManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.assets = Assets()
        self.reset()

    def reset(self):
        self.wave = 0
        self.score = 0
        self.coins = 0
        self.combo = 0
        self.combo_timer = 0
        self.kill_feed = []
        self.state = 'playing'
        self.wave_timer = 0
        self.wave_transition = False
        self.wave_transition_timer = 0
        self.show_shop = False
        self.show_upgrade = False
        self.paused = False
        self.slow_mo = False
        self.slow_mo_timer = 0
        self.game_time = 0

        self.arena = Arena(ARENA_W, ARENA_H)
        self.tilemap = TileMap(self.arena)
        self.spatial_hash = SpatialHash(CELL_SIZE)
        self.particles = ParticleSystem()
        self.effects = EffectsManager(self.screen)
        self.lighting = LightingSystem(ARENA_W, ARENA_H)
        self.camera = Camera(SCREEN_W, SCREEN_H, ARENA_W * TILE_SIZE, ARENA_H * TILE_SIZE)

        self.weapon_manager = WeaponManager()
        self.ability_manager = AbilityManager()
        self.upgrade_system = UpgradeSystem()

        spawn = self.arena.get_spawn()
        self.player = Player(spawn[0], spawn[1], self.weapon_manager, self.ability_manager)

        self.enemy_manager = EnemyManager(self.arena, self.spatial_hash)
        self.boss_manager = BossManager(self.arena)

        self.hud = HUD(self.screen, self.player, self)
        self.shop = Shop(self.screen, self)
        self.upgrade_options = []

        self.surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.start_wave()

    def start_wave(self):
        self.wave += 1
        self.wave_transition = True
        self.wave_transition_timer = WAVE_TRANSITION_TIME
        if self.wave % 5 == 0:
            boss_spawn = self.arena.get_spawn()
            self.boss_manager.spawn_boss((self.wave // 5 - 1) % 3, boss_spawn)
        else:
            count = 3 + self.wave * 2
            tier = min(2, (self.wave - 1) // 3)
            self.enemy_manager.spawn_wave(count, tier, self.player)

    def add_kill_feed(self, text):
        self.kill_feed.append({'text': text, 'timer': 3.0})
        if len(self.kill_feed) > 5:
            self.kill_feed.pop(0)

    def add_coin(self, amount):
        self.coins += amount

    def add_score(self, amount):
        self.score += amount * (1 + self.combo // 5)

    def increment_combo(self):
        self.combo += 1
        self.combo_timer = COMBO_TIMEOUT

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_shop or self.show_upgrade:
                        pass
                    else:
                        self.paused = not self.paused
                if self.paused:
                    if event.key == pygame.K_r:
                        self.reset()
                        return 'playing'
                    if event.key == pygame.K_q:
                        return 'menu'
            if self.show_shop:
                result = self.shop.handle_event(event)
                if result == 'close':
                    self.show_shop = False
                    if self.wave % 3 == 0:
                        self.show_upgrade = True
                        self.upgrade_options = self.upgrade_system.get_options(3)
            elif self.show_upgrade:
                result = self.handle_upgrade_event(event)
            elif not self.paused:
                self.player.handle_event(event)
        return 'playing'

    def handle_upgrade_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                idx = event.key - pygame.K_1
                if idx < len(self.upgrade_options):
                    self.upgrade_system.apply(self.upgrade_options[idx], self.player, self)
                    self.show_upgrade = False

    def update(self, dt):
        if self.paused or self.show_shop or self.show_upgrade:
            return

        if self.slow_mo:
            dt *= SLOW_MO_FACTOR
            self.slow_mo_timer -= dt / SLOW_MO_FACTOR
            if self.slow_mo_timer <= 0:
                self.slow_mo = False

        self.game_time += dt

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        for kf in self.kill_feed[:]:
            kf['timer'] -= dt
            if kf['timer'] <= 0:
                self.kill_feed.remove(kf)

        if self.wave_transition:
            self.wave_transition_timer -= dt
            if self.wave_transition_timer <= 0:
                self.wave_transition = False

        mx, my = pygame.mouse.get_pos()
        world_mx = mx + self.camera.x
        world_my = my + self.camera.y

        self.player.update(dt, self.tilemap, self.spatial_hash, world_mx, world_my,
                           self.particles, self.effects)

        bullets = self.player.weapon_manager.get_bullets()
        enemy_bullets = []

        self.spatial_hash.clear()
        self.spatial_hash.insert(self.player, self.player.x, self.player.y)
        for e in self.enemy_manager.enemies:
            self.spatial_hash.insert(e, e.x, e.y)
        for b in self.boss_manager.bosses:
            self.spatial_hash.insert(b, b.x, b.y)

        dead_enemies = self.enemy_manager.update(dt, self.player, self.tilemap,
                                                  self.particles, self.effects,
                                                  bullets, enemy_bullets)
        for e in dead_enemies:
            self.add_kill_feed(f"{e.name} killed")
            self.add_score(e.score_value)
            self.add_coin(e.coin_drop)
            self.increment_combo()
            self.particles.spawn_burst(e.x, e.y, e.color, 20)

        dead_bosses = self.boss_manager.update(dt, self.player, self.tilemap,
                                                self.particles, self.effects,
                                                bullets, enemy_bullets)
        for b in dead_bosses:
            self.add_kill_feed(f"BOSS {b.name} SLAIN!")
            self.add_score(b.score_value)
            self.add_coin(b.coin_drop)
            self.slow_mo = True
            self.slow_mo_timer = SLOW_MO_DURATION
            self.effects.flash(WHITE, 0.3)
            self.particles.spawn_burst(b.x, b.y, b.color, 80)

        for eb in enemy_bullets:
            ex, ey = eb.get('x', 0), eb.get('y', 0)
            if math.dist((ex, ey), (self.player.x, self.player.y)) < self.player.radius + eb.get('radius', 4):
                if not self.player.invincible:
                    dmg = eb.get('damage', 10)
                    self.player.take_damage(dmg, self.effects, self.particles)

        self.tilemap.update(dt, self.player, self.particles)
        self.particles.update(dt)
        self.lighting.update(dt, self.player, self.enemy_manager.enemies + self.boss_manager.bosses)
        self.effects.update(dt)
        self.camera.follow(self.player.x, self.player.y, dt)

        all_dead = (len(self.enemy_manager.enemies) == 0 and
                    len(self.boss_manager.bosses) == 0 and
                    not self.wave_transition)
        if all_dead and self.state == 'playing':
            self.end_wave()

        if self.player.hp <= 0:
            self.state = 'dead'

    def end_wave(self):
        if self.wave % 3 == 0:
            self.show_shop = True
            self.shop.restock()
        elif self.wave % 3 == 1 and self.wave > 1:
            self.show_upgrade = True
            self.upgrade_options = self.upgrade_system.get_options(3)
        self.start_wave()

    def draw(self):
        self.surface.fill(BLACK)

        self.tilemap.draw(self.surface, self.camera)
        self.particles.draw(self.surface, self.camera)
        self.player.draw(self.surface, self.camera)
        self.enemy_manager.draw(self.surface, self.camera)
        self.boss_manager.draw(self.surface, self.camera)
        self.player.weapon_manager.draw_bullets(self.surface, self.camera)

        light_surf = self.lighting.render(self.camera)
        self.surface.blit(light_surf, (0, 0), special_flags=pygame.BLEND_MULT)

        self.screen.blit(self.surface, (0, 0))

        self.hud.draw(self.camera)
        self.effects.draw_overlay()

        if self.wave_transition:
            self.draw_wave_banner()

        if self.paused:
            self.draw_pause()

        if self.show_shop:
            self.shop.draw()

        if self.show_upgrade:
            self.draw_upgrade_screen()

        pygame.display.flip()

    def draw_wave_banner(self):
        alpha = min(255, int(255 * (self.wave_transition_timer / WAVE_TRANSITION_TIME)))
        surf = pygame.Surface((SCREEN_W, 100), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 180))
        font = pygame.font.SysFont('monospace', 48, bold=True)
        if self.wave % 5 == 0:
            text = f"BOSS WAVE {self.wave}"
            color = (255, 60, 60)
        else:
            text = f"WAVE {self.wave}"
            color = (255, 220, 60)
        t = font.render(text, True, color)
        surf.blit(t, (SCREEN_W//2 - t.get_width()//2, 25))
        surf.set_alpha(alpha)
        self.screen.blit(surf, (0, SCREEN_H//2 - 50))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont('monospace', 48, bold=True)
        f2 = pygame.font.SysFont('monospace', 24)
        t = font.render("PAUSED", True, WHITE)
        self.screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 260))
        lines = ["R - Restart", "Q - Quit to Menu", "ESC - Resume"]
        for i, l in enumerate(lines):
            s = f2.render(l, True, GRAY)
            self.screen.blit(s, (SCREEN_W//2 - s.get_width()//2, 340 + i*35))

    def draw_upgrade_screen(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont('monospace', 36, bold=True)
        f2 = pygame.font.SysFont('monospace', 20)
        f3 = pygame.font.SysFont('monospace', 16)
        t = font.render("CHOOSE AN UPGRADE", True, (255, 220, 60))
        self.screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 80))
        rarity_colors = {'common': (180,180,180), 'uncommon': (60,200,60), 'rare': (60,120,255), 'legendary': (200,60,255)}
        for i, opt in enumerate(self.upgrade_options):
            x = 160 + i * 330
            y = 180
            rc = rarity_colors.get(opt.get('rarity','common'), WHITE)
            pygame.draw.rect(self.screen, (30,30,50), (x, y, 280, 320), border_radius=12)
            pygame.draw.rect(self.screen, rc, (x, y, 280, 320), 3, border_radius=12)
            num = f2.render(f"[{i+1}]", True, WHITE)
            self.screen.blit(num, (x+10, y+10))
            name = f2.render(opt.get('name','???'), True, rc)
            self.screen.blit(name, (x+140 - name.get_width()//2, y+50))
            rtext = f3.render(opt.get('rarity','common').upper(), True, rc)
            self.screen.blit(rtext, (x+140 - rtext.get_width()//2, y+80))
            desc = opt.get('desc','')
            words = desc.split()
            lines = []
            line = ''
            for w in words:
                if len(line + w) > 22:
                    lines.append(line)
                    line = w + ' '
                else:
                    line += w + ' '
            if line:
                lines.append(line)
            for j, l in enumerate(lines):
                s = f3.render(l.strip(), True, (200,200,200))
                self.screen.blit(s, (x+10, y+120 + j*22))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            result = self.handle_events()
            if result == 'quit':
                return 'quit'
            if result == 'menu':
                return 'menu'
            if self.state == 'dead':
                return 'dead'
            self.update(dt)
            self.draw()