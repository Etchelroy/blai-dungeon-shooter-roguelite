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