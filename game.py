import pygame
import math
import random
import sys

from constants import *
from arena import Arena
from player import Player
from enemies import Grunt, Archer, Shield, Berserker, Bomber, Swarm, Healer, Tank, Ghost, Summoner
from bosses import GolemBoss, NecromancerBoss, DragonBoss
from hud import HUD
from wave_manager import WaveManager
from coins import CoinManager
from particles import ParticleSystem
from camera import Camera

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'playing'  # 'playing', 'dead', 'paused'

        self.arena = Arena(28, 28)
        self.camera = Camera(SCREEN_W, SCREEN_H)
        self.particles = ParticleSystem()
        self.coin_manager = CoinManager()
        self.hud = HUD()

        px, py = self.arena.player_spawn
        self.player = Player(px, py)
        self.player._arena_ref = self.arena

        self.enemies = []
        self.projectiles = []
        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 3.0

        self.wave_manager = WaveManager(self.arena, self.enemies)
        self.wave_manager.state = 'idle'
        self.wave_manager.between_wave_timer = 2.9

        self.dead_screen_timer = 0.0
        self.font_lg = pygame.font.SysFont('impact', 64)
        self.font_md = pygame.font.SysFont('arial', 28)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'
            if self.state == 'dead':
                if event.key == pygame.K_RETURN:
                    return 'menu'
        return None

    def _get_solid_rects(self):
        return self.arena.get_solid_rects()

    def _get_enemy_rects(self):
        return [(e, e.rect) for e in self.enemies if e.alive]

    def update(self, dt):
        if self.state == 'dead':
            self.dead_screen_timer += dt
            return

        # Player update
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        wx, wy = self.camera.screen_to_world(mx, my)
        mouse_buttons = pygame.mouse.get_pressed()

        solid_rects = self._get_solid_rects()
        enemy_rects = self._get_enemy_rects()

        player_projs, melee_hits = self.player.update(
            dt, keys, (wx, wy), mouse_buttons, solid_rects, self.particles
        )
        self.projectiles.extend(player_projs)

        # Melee hits on enemies
        if melee_hits:
            for e in self.enemies:
                if e.alive and e.rect.colliderect(melee_hits):
                    dmg = self.player.melee_damage
                    e.take_damage(dmg, self.particles)
                    self.particles.emit('hit', e.rect.centerx, e.rect.centery, 6, (255,200,100))

        # Enemy updates
        dead_enemies = []
        for e in self.enemies:
            if not e.alive:
                dead_enemies.append(e)
                continue
            eprojs = e.update(dt, self.player.rect, solid_rects, self.particles)
            if eprojs:
                self.projectiles.extend(eprojs)

        for e in dead_enemies:
            self.enemies.remove(e)
            self.wave_manager.on_enemy_killed(e)
            coins = getattr(e, 'coin_drop', 1)
            self.coin_manager.spawn(e.rect.centerx, e.rect.centery, coins)
            self.combo += 1
            self.combo_timer = self.combo_timeout
            self.player.combo = self.combo
            self.score += int(getattr(e, 'score_value', 10) * max(1, self.combo // 3))
            self.hud.add_kill(f'{type(e).__name__} slain!')
            self.hud.combo_display_timer = 2.0

        # Combo decay
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
                self.player.combo = 0

        # Projectile updates
        new_projs = []
        for p in self.projectiles:
            p.update(dt)
            if not p.alive:
                continue
            # Wall collision
            hit_wall = False
            for wr in solid_rects:
                if p.rect.colliderect(wr):
                    p.on_wall_hit(self.particles)
                    hit_wall = True
                    break
            if hit_wall:
                continue

            # Player projectiles vs enemies
            if p.owner == 'player':
                for e in self.enemies:
                    if e.alive and p.rect.colliderect(e.rect):
                        dmg = p.damage
                        e.take_damage(dmg, self.particles)
                        p.on_hit(self.particles)
                        if not p.piercing:
                            break
            # Enemy projectiles vs player
            elif p.owner == 'enemy':
                if p.rect.colliderect(self.player.rect) and not self.player.dashing:
                    self.player.take_damage(p.damage)
                    p.on_hit(self.particles)
                    self.particles.emit('hit', p.rect.centerx, p.rect.centery, 5, (255,80,80))

            if p.alive:
                new_projs.append(p)
        self.projectiles = new_projs

        # Hazard checks
        hazard_effects = self.arena.check_hazards(self.player.rect)
        for eff in hazard_effects:
            if eff.get('type') == 'fire':
                self.player.take_damage(eff['damage'] * dt)
                self.particles.emit('fire', self.player.rect.centerx, self.player.rect.centery, 2, (255,100,0))
            elif eff.get('type') == 'slow':
                self.player.speed_multiplier = eff.get('factor', 0.5)
            elif eff.get('type') == 'spikes':
                self.player.take_damage(eff['damage'] * dt)
            elif eff.get('type') == 'poison':
                self.player.apply_poison(eff['damage'], eff.get('duration', 3.0))
        if not hazard_effects:
            self.player.speed_multiplier = 1.0

        # Coins
        collected = self.coin_manager.update(dt, self.player.rect)

        # Arena update
        self.arena.update(dt)

        # Particles
        self.particles.update(dt)

        # HUD
        self.hud.update(dt)

        # Wave manager
        self.wave_manager.update(dt, self.player, self.hud, self.particles)

        # Camera follow player
        self.camera.follow(self.player.rect.centerx, self.player.rect.centery,
                           self.arena.pixel_width, self.arena.pixel_height)

        # Player death
        if self.player.hp <= 0 and self.state == 'playing':
            self.state = 'dead'
            self.dead_screen_timer = 0.0

    def draw(self):
        self.screen.fill((10, 8, 12))

        self.arena.draw(self.screen, self.camera)

        # Draw projectiles
        for p in self.projectiles:
            p.draw(self.screen, self.camera)

        # Draw enemies
        for e in self.enemies:
            if e.alive:
                e.draw(self.screen, self.camera)

        # Draw player
        self.player.draw(self.screen, self.camera)

        # Draw coins
        self.coin_manager.draw(self.screen, self.camera)

        # Draw particles
        self.particles.draw(self.screen, self.camera)

        # HUD
        self.hud.draw(self.screen, self.player, self.wave_manager.wave, self.score, self.coin_manager.total)

        # Wave text
        if self.wave_manager.state == 'idle' and self.wave_manager.wave > 0:
            wt = self.font_md.render(self.wave_manager.get_wave_text(), True, (100, 255, 100))
            self.screen.blit(wt, (SCREEN_W//2 - wt.get_width()//2, SCREEN_H//2 - 100))

        # Dead screen
        if self.state == 'dead':
            overlay =