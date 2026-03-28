import pygame
import random
import math

class WaveManager:
    def __init__(self, arena, enemy_group):
        self.arena = arena
        self.enemy_group = enemy_group
        self.wave = 0
        self.state = 'idle'  # 'idle', 'spawning', 'active', 'boss', 'complete'
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.spawn_delay = 0.4
        self.between_wave_timer = 0.0
        self.between_wave_delay = 3.0
        self.boss_spawned = False
        self.boss_ref = None
        self.enemies_killed = 0
        self.total_this_wave = 0

    def start_next_wave(self):
        self.wave += 1
        self.boss_spawned = False
        self.boss_ref = None
        self.enemies_killed = 0
        self._build_spawn_queue()
        self.total_this_wave = len(self.spawn_queue)
        self.state = 'spawning'

    def _build_spawn_queue(self):
        from enemies import (Grunt, Archer, Shield, Berserker, Bomber,
                             Swarm, Healer, Tank, Ghost, Summoner)
        w = self.wave
        queue = []

        if w % 5 == 0:
            self.state = 'boss'
            return

        tier1 = [Grunt, Archer, Swarm]
        tier2 = [Shield, Berserker, Bomber, Ghost]
        tier3 = [Tank, Healer, Summoner]

        count = 5 + w * 3
        for _ in range(count):
            r = random.random()
            if w < 3 or r < 0.5:
                cls = random.choice(tier1)
            elif w < 6 or r < 0.8:
                cls = random.choice(tier2)
            else:
                cls = random.choice(tier3)
            queue.append(cls)

        random.shuffle(queue)
        self.spawn_queue = queue

    def spawn_boss(self, hud):
        from bosses import GolemBoss, NecromancerBoss, DragonBoss
        boss_classes = [GolemBoss, NecromancerBoss, DragonBoss]
        idx = (self.wave // 5 - 1) % len(boss_classes)
        pos = self.arena.player_spawn
        bx = pos[0] + 200
        by = pos[1]
        boss = boss_classes[idx](bx, by)
        self.enemy_group.append(boss)
        self.boss_ref = boss
        self.boss_spawned = True
        hud.set_boss(boss.name, boss.hp, boss.max_hp)
        return boss

    def on_enemy_killed(self, enemy):
        self.enemies_killed += 1

    def update(self, dt, player, hud, particles):
        if self.state == 'idle':
            self.between_wave_timer += dt
            if self.between_wave_timer >= self.between_wave_delay:
                self.between_wave_timer = 0
                self.start_next_wave()

        elif self.state == 'spawning':
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay and self.spawn_queue:
                self.spawn_timer = 0
                cls = self.spawn_queue.pop(0)
                pos = self.arena.get_random_spawn()
                enemy = cls(pos[0], pos[1])
                self.enemy_group.append(enemy)
            if not self.spawn_queue:
                self.state = 'active'

        elif self.state == 'active':
            alive = [e for e in self.enemy_group if e.alive]
            if not alive:
                self.state = 'idle'
                self.between_wave_timer = 0

        elif self.state == 'boss':
            if not self.boss_spawned:
                self.spawn_boss(hud)
            else:
                if self.boss_ref and not self.boss_ref.alive:
                    hud.clear_boss()
                    self.boss_ref = None
                    self.state = 'idle'
                    self.between_wave_timer = 0
                elif self.boss_ref:
                    hud.set_boss(self.boss_ref.name, self.boss_ref.hp, self.boss_ref.max_hp)

    def get_wave_text(self):
        if self.state == 'idle':
            return f'Wave {self.wave} complete!'
        elif self.state == 'boss':
            return f'BOSS WAVE {self.wave}!'
        return f'Wave {self.wave}'