import pygame
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

from settings import *
from camera import Camera
from arena import Arena
from player import Player
from waves import WaveManager
from hud import HUD
from effects import EffectManager
from particles import ParticleSystem
from lighting import LightingSystem
from ui import UIManager
from collision import SpatialHash
from audio import AudioManager
from projectiles import ProjectileManager
from shop import ShopManager
from upgrades import UpgradeManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("INFERNO DUNGEON")
        self.clock = pygame.time.Clock()
        self.state = STATE_MAIN_MENU
        self.running = True
        self.dt = 0.0
        self.raw_dt = 0.0
        self.time_scale = 1.0
        self.slow_mo_timer = 0.0
        self.frame_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self._init_systems()

    def _init_systems(self):
        self.audio = AudioManager()
        self.effects = EffectManager(self.screen)
        self.particles = ParticleSystem()
        self.ui = UIManager(self)
        self.spatial_hash = SpatialHash(CELL_SIZE)
        self.upgrade_manager = UpgradeManager()
        self.shop_manager = ShopManager(self)
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.coins = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.kill_feed = []
        self.wave_num = 0
        self.run_stats = {
            'kills': 0, 'damage_dealt': 0, 'damage_taken': 0,
            'time': 0.0, 'waves': 0, 'boss_kills': 0
        }
        self.particles.clear()
        self.effects.reset()
        self.arena = Arena()
        self.arena.generate(1)
        self.lighting = LightingSystem(self.arena)
        self.camera = Camera(SCREEN_W, SCREEN_H, self.arena.pixel_w, self.arena.pixel_h)
        self.projectile_manager = ProjectileManager(self.particles, self.effects)
        self.player = Player(
            self.arena.spawn_x, self.arena.spawn_y,
            self.particles, self.effects, self.projectile_manager, self.audio
        )
        self.camera.set_target(self.player)
        self.wave_manager = WaveManager(self, self.arena)
        self.hud = HUD(self)
        self.enemies = []
        self.bosses = []
        self.spatial_hash.clear()
        self.upgrade_manager.reset()
        self.pending_powerups = []
        self.shop_open = False
        self.post_wave_timer = 0.0

    def start_game(self):
        self.reset_game()
        self.state = STATE_PLAYING
        self.wave_manager.start_wave(1)
        self.audio.play_music('game')

    def trigger_slow_mo(self, duration=2.0, scale=0.2):
        self.time_scale = scale
        self.slow_mo_timer = duration

    def add_score(self, points):
        self.combo += 1
        self.combo_timer = COMBO_TIMEOUT
        multiplier = 1 + (self.combo // 5) * 0.5
        earned = int(points * multiplier)
        self.score += earned
        return earned

    def add_kill(self, enemy_name):
        self.run_stats['kills'] += 1
        self.kill_feed.append({'name': enemy_name, 'timer': KILL_FEED_TIME})
        if len(self.kill_feed) > MAX_KILL_FEED:
            self.kill_feed.pop(0)

    def run(self):
        while self.running:
            self.raw_dt = self.clock.tick(FPS) / 1000.0
            self.raw_dt = min(self.raw_dt, MAX_DT)
            if self.slow_mo_timer > 0:
                self.slow_mo_timer -= self.raw_dt
                if self.slow_mo_timer <= 0:
                    self.time_scale = 1.0
                    self.slow_mo_timer = 0
            self.dt = self.raw_dt * self.time_scale
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_SHOP:
                        self.state = STATE_PLAYING
            self.ui.handle_event(event)
            if self.state == STATE_PLAYING:
                self.player.handle_event(event)

    def _update(self):
        if self.state == STATE_MAIN_MENU:
            self.ui.update_main_menu(self.raw_dt)
        elif self.state == STATE_PLAYING:
            self._update_game()
        elif self.state == STATE_PAUSED:
            pass
        elif self.state == STATE_SHOP:
            self.shop_manager.update(self.raw_dt)
        elif self.state == STATE_POWERUP:
            pass
        elif self.state == STATE_DEATH:
            self.ui.update_death(self.raw_dt)

    def _update_game(self):
        dt = self.dt
        self.run_stats['time'] += self.raw_dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
        for kf in self.kill_feed[:]:
            kf['timer'] -= dt
            if kf['timer'] <= 0:
                self.kill_feed.remove(kf)
        self.spatial_hash.clear()
        self.spatial_hash.insert(self.player, self.player.rect)
        for e in self.enemies:
            self.spatial_hash.insert(e, e.rect)
        for b in self.bosses:
            self.spatial_hash.insert(b, b.rect)
        self.player.update(dt, self.arena, self.enemies + self.bosses, self.spatial_hash)
        for e in self.enemies[:]:
            e.update(dt, self.player, self.arena, self.particles, self.spatial_hash)
            if e.dead:
                pts = self.add_score(e.score_value)
                self.coins += e.coin_drop
                self.add_kill(e.name)
                e.on_death(self.particles, self.effects)
                self.run_stats['damage_dealt'] += e.max_hp
                self.enemies.remove(e)
        for b in self.bosses[:]:
            b.update(dt, self.player, self.arena, self.particles, self.spatial_hash, self.projectile_manager)
            if b.dead:
                pts = self.add_score(b.score_value)
                self.coins += b.coin_drop
                self.add_kill(b.name)
                b.on_death(self.particles, self.effects)
                self.run_stats['boss_kills'] += 1
                self.bosses.remove(b)
                self.trigger_slow_mo(2.0, 0.15)
                self.effects.screen_flash((255, 200, 50), 0.5)
        self.projectile_manager.update(dt, self.arena, self.enemies + self.bosses, self.player, self.spatial_hash)
        self.particles.update(dt)
        self.lighting.update(dt, self.player, self.enemies + self.bosses)
        self.camera.update(dt)
        self.effects.update(dt)
        self.arena.update(dt, self.player, self.particles, self.effects)
        self.wave_manager.update(dt)
        if self.player.hp <= 0:
            self.state = STATE_DEATH
            self.ui.init_death_screen()
            self.audio.play_music('none')

    def _draw(self):
        self.frame_surface.fill(COLOR_BG)
        if self.state == STATE_MAIN_MENU:
            self.ui.draw_main_menu(self.frame_surface)
        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_SHOP, STATE_POWERUP):
            self._draw_game()
            if self.state == STATE_PAUSED:
                self.ui.draw_pause(self.frame_surface)
            elif self.state == STATE_SHOP:
                self.shop_manager.draw(self.frame_surface)
            elif self.state == STATE_POWERUP:
                self.ui.draw_powerup(self.frame_surface, self.pending_powerups)
        elif self.state == STATE_DEATH:
            self._draw_game()
            self.ui.draw_death(self.frame_surface)
        elif self.state == STATE_CONTROLS:
            self.ui.draw_controls(self.frame_surface)
        self.effects.draw_post(self.frame_surface)
        self.screen.blit(self.frame_surface, (0, 0))
        pygame.display.flip()

    def _draw_game(self):
        surf = self.frame_surface
        cx, cy = self.camera.get_offset()
        self.arena.draw(surf, cx, cy, self.camera)
        for e in self.enemies:
            e.draw(surf, cx, cy)
        for b in self.bosses:
            b.draw(surf, cx, cy)
        self.projectile_manager.draw(surf, cx, cy)
        self.player.draw(surf, cx, cy)
        self.particles.draw(surf, cx, cy)
        self.lighting.draw(surf, cx, cy)
        self.hud.draw(surf)

if __name__ == '__main__':
    game = Game()
    game.run()