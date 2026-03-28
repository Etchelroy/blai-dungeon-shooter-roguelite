import pygame, math, random
from settings import *
from particles import ParticleSystem
from utils import distance, angle_to

class BossBase:
    def __init__(self, x, y, ps: ParticleSystem):
        self.x = x; self.y = y
        self.ps = ps
        self.hp = 500; self.max_hp = 500
        self.phase = 0
        self.alive = True
        self.radius = 30
        self.vx = 0; self.vy = 0
        self.flash_timer = 0
        self.anim_timer = 0
        self.attack_cooldown = 0
        self.projectiles = []
        self.vulnerable = True
        self.invuln_timer = 0
        self.score_value = 5000
        self.coin_value = 50
        self.name = "BOSS"
        self.color = (200, 50, 50)
        self.phase_thresholds = [0.66, 0.33]
        self.death_sequence = False
        self.death_timer = 0

    def get_phase(self):
        ratio = self.hp / self.max_hp
        if ratio > self.phase_thresholds[0]:
            return 0
        elif ratio > self.phase_thresholds[1]:
            return 1
        else:
            return 2

    def take_damage(self, amount, kx=0, ky=0):
        if not self.vulnerable or self.invuln_timer > 0:
            return False
        old_phase = self.get_phase()
        self.hp -= amount
        self.flash_timer = 0.08
        new_phase = self.get_phase()
        if new_phase != old_phase:
            self.phase = new_phase
            self.on_phase_change(new_phase)
        if self.hp <= 0:
            self.hp = 0
            self.start_death()
            return True
        return False

    def on_phase_change(self, phase):
        self.invuln_timer = 2.0
        self.vulnerable = False
        for _ in range(20):
            a = random.uniform(0, math.tau)
            self.ps.emit(self.x, self.y, math.cos(a)*150, math.sin(a)*150,
                         self.color, 0.8, random.randint(4, 8))

    def start_death(self):
        self.death_sequence = True
        self.death_timer = 3.0
        self.vulnerable = False

    def update(self, dt, player, tilemap, spatial_hash):
        self.anim_timer += dt
        self.flash_timer = max(0, self.flash_timer - dt)
        self.invuln_timer = max(0, self.invuln_timer - dt)
        if self.invuln_timer <= 0:
            self.vulnerable = True
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        if self.death_sequence:
            self.death_timer -= dt
            for _ in range(3):
                a = random.uniform(0, math.tau)
                r = random.uniform(0, self.radius)
                self.ps.emit(
                    self.x + math.cos(a)*r, self.y + math.sin(a)*r,
                    math.cos(a)*100, math.sin(a)*100,
                    (255, random.randint(100, 200), 20), random.uniform(0.3, 0.8),
                    random.randint(4, 10)
                )
            if self.death_timer <= 0:
                self.alive = False
            return
        for p in self.projectiles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
            if p['life'] <= 0:
                self.projectiles.remove(p)

    def draw_hp_bar(self, surf):
        bar_w = 400; bar_h = 20
        x = SCREEN_W//2 - bar_w//2; y = 30
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (40, 0, 0), (x, y, bar_w, bar_h))
        phase_cols = [(200, 50, 50), (220, 150, 30), (255, 80, 200)]
        col = phase_cols[min(self.phase, 2)]
        pygame.draw.rect(surf, col, (x, y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surf, (255, 200, 200), (x, y, bar_w, bar_h), 2)
        for i, thresh in enumerate(self.phase_thresholds):
            tx = x + int(bar_w * thresh)
            pygame.draw.line(surf, (255, 255, 255), (tx, y), (tx, y + bar_h), 2)
        font = pygame.font.SysFont('consolas', 16, bold=True)
        label = font.render(f"{self.name}  {self.hp}/{self.max_hp}", True, (255, 220, 220))
        surf.blit(label, (SCREEN_W//2 - label.get_width()//2, y + 2))
        if not self.vulnerable:
            inv_label = font.render("[ INVULNERABLE ]", True, (100, 200, 255))
            surf.blit(inv_label, (SCREEN_W//2 - inv_label.get_width()//2, y + bar_h + 4))

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        pygame.draw.circle(surf, col, (int(sx), int(sy)), self.radius)
        for p in self.projectiles:
            px, py = cam.world_to_screen(p['x'], p['y'])
            pygame.draw.circle(surf, p.get('color', (255, 200, 50)), (int(px), int(py)), p.get('r', 6))


class BossSlimeKing(BossBase):
    def __init__(self, x, y, ps):
        super(