import pygame
import math
import random
from particles import Particle

class BossProjectile:
    def __init__(self, x, y, vx, vy, color, radius, damage, lifetime=4.0):
        self.pos = [x, y]
        self.vel = [vx, vy]
        self.color = color
        self.radius = radius
        self.damage = damage
        self.lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.pos[0], self.pos[1])
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
        inner = tuple(min(255, c+80) for c in self.color)
        pygame.draw.circle(surface, inner, (int(sx), int(sy)), max(1, self.radius-3))

    def get_rect(self):
        return pygame.Rect(self.pos[0]-self.radius, self.pos[1]-self.radius,
                          self.radius*2, self.radius*2)


class Boss:
    def __init__(self, x, y, name, max_hp, phase_thresholds):
        self.pos = [float(x), float(y)]
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.phase = 1
        self.phase_thresholds = phase_thresholds  # e.g. [0.66, 0.33]
        self.projectiles = []
        self.alive = True
        self.death_timer = 0
        self.dying = False
        self.invuln = False
        self.invuln_timer = 0
        self.attack_timer = 0
        self.move_timer = 0
        self.target_pos = [x, y]
        self.speed = 80
        self.iframes = 0
        self.radius = 40
        self.phase_transition_timer = 0
        self.phase_transitioning = False
        self.anim_timer = 0
        self.enrage = False

    def take_damage(self, dmg):
        if self.invuln or self.iframes > 0 or self.phase_transitioning:
            return False
        self.hp -= dmg
        self.iframes = 0.1
        if self.hp <= 0:
            self.hp = 0
            if not self.dying:
                self.dying = True
            return True
        return False

    def check_phase(self):
        ratio = self.hp / self.max_hp
        new_phase = 1
        for i, threshold in enumerate(self.phase_thresholds):
            if ratio <= threshold:
                new_phase = i + 2
        if new_phase > self.phase and not self.phase_transitioning:
            self.phase = new_phase
            self.phase_transitioning = True
            self.phase_transition_timer = 2.0
            self.invuln = True
            return True
        return False

    def update_base(self, dt, player, particles):
        self.anim_timer += dt
        if self.iframes > 0:
            self.iframes -= dt
        if self.phase_transitioning:
            self.phase_transition_timer -= dt
            # Explosion particles
            if random.random() < 0.3:
                angle = random.uniform(0, math.pi*2)
                speed = random.uniform(50, 150)
                p = Particle(self.pos[0], self.pos[1],
                            math.cos
I'll analyze what's been done and implement the remaining systems needed to pass all acceptance criteria.

# filename: hud.py
```python
import pygame
import math

class HUD:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.kill_feed = []
        self.kill_feed_timer = []
        self.font_large = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14)
        self.combo_anim = 0

    def add_kill(self, enemy_name):
        self.kill_feed.insert(0, f"Killed {enemy_name}")
        self.kill_feed_timer.insert(0, 3.0)
        if len(self.kill_feed) > 5:
            self.kill_feed.pop()
            self.kill_feed_timer.pop()

    def update(self, dt):
        self.combo_anim = max(0, self.combo_anim - dt * 2)
        for i in range(len(self.kill_feed_timer)-1, -1, -1):
            self.kill_feed_timer[i] -= dt
            if self.kill_feed_timer[i] <= 0:
                self.kill_feed.pop(i)
                self.kill_feed_timer.pop(i)

    def draw(self, surface, player, wave, score, coins, boss=None):
        self._draw_hp_bar(surface, player)
        self._draw_dash_cooldown(surface, player)
        self._draw_weapon_info(surface, player)
        self._draw_wave_score(surface, wave, score, coins)
        self._draw_combo(surface, player)
        self._draw_minimap(surface, player)
        self._draw_kill_feed(surface)
        self._draw_secondary(surface, player)
        if boss:
            self._draw_boss_bar(surface, boss)

    def _draw_hp_bar(self, surface, player):
        x, y, w, h = 20, 20, 200, 20
        pygame.draw.rect(surface, (60, 0, 0), (x, y, w, h))
        hp_ratio = max(0, player.hp / player.max_hp)
        color = (0, 200, 0) if hp_ratio > 0.5 else (200, 200, 0) if hp_ratio > 0.25 else (200, 0, 0)
        pygame.draw.rect(surface, color, (x, y, int(w * hp_ratio), h))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2)
        txt = self.font_small.render(f"HP {int(player.hp)}/{player.max_hp}", True, (255, 255, 255))
        surface.blit(txt, (x + 5, y + 2))

        # Shield bar if any
        if hasattr(player, 'shield') and player.shield > 0:
            sy = y + 24
            pygame.draw.rect(surface, (0, 0, 80), (x, sy, w, 10))
            sr = min(1, player.shield / 50)
            pygame.draw.rect(surface, (100, 100, 255), (x, sy, int(w * sr), 10))
            pygame.draw.rect(surface, (150, 150, 255), (x, sy, w, 10), 1)

    def _draw_dash_cooldown(self, surface, player):
        x, y = 20, 60
        cd = getattr(player, 'dash_cooldown', 0)
        max_cd = getattr(player, 'dash_cooldown_max', 1.0)
        ratio = 1.0 - min(1, cd / max_cd) if max_cd > 0 else 1.0
        color = (0, 200, 255) if ratio >= 1.0 else (100, 100, 150)
        pygame.draw.rect(surface, (30, 30, 60), (x, y, 100, 12))
        pygame.draw.rect(surface, color, (x, y, int(100 * ratio), 12))
        pygame.draw.rect(surface, (150, 150, 200), (x, y, 100, 12), 1)
        txt = self.font_small.render("DASH", True, (200, 200, 255))
        surface.blit(txt, (x + 30, y - 1))

    def _draw_weapon_info(self, surface, player):
        x, y = 20, 85
        wname = "No Weapon"
        ammo_str = ""
        if hasattr(player, 'weapons') and player.weapons:
            idx = getattr(player, 'weapon_index', 0)
            w = player.weapons[idx]
            wname = w.name if hasattr(w, 'name') else str(type(w).__name__)
            ammo = getattr(w, 'ammo', None)
            max_ammo = getattr(w, 'max_ammo', None)
            reload_t = getattr(w, 'reload_timer', 0)
            if ammo is not None:
                if reload_t > 0:
                    ammo_str = "RELOADING..."
                else:
                    ammo_str = f"{ammo}/{max_ammo}"
        txt = self.font_med.render(wname, True, (255, 220, 100))
        surface.blit(txt, (x, y))
        if ammo_str:
            atxt = self.font_small.render(ammo_str, True, (200, 200, 200))
            surface.blit(atxt, (x, y + 20))

    def _draw_wave_score(self, surface, wave, score, coins):
        wtxt = self.font_large.render(f"Wave {wave}", True, (255, 255, 100))
        surface.blit(wtxt, (self.sw // 2 - wtxt.get_width() // 2, 10))
        stxt = self.font_med.render(f"Score: {score}", True, (200, 200, 255))
        surface.blit(stxt, (self.sw - 160, 20))
        ctxt = self.font_med.render(f"Coins: {coins}", True, (255, 215, 0))
        surface.blit(ctxt, (self.sw - 160, 44))

    def _draw_combo(self, surface, player):
        combo = getattr(player, 'combo', 0)
        if combo > 1:
            scale = 1.0 + self.combo_anim * 0.3
            size = int(28 * scale)
            try:
                f = pygame.font.SysFont('Arial', size, bold=True)
            except:
                f = self.font_large
            alpha = min(255, combo * 30 + 150)
            txt = f.render(f"x{combo} COMBO!", True, (255, 100, 0))
            surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, 45))

    def _draw_secondary(self, surface, player):
        if not hasattr(player, 'secondary') or player.secondary is None:
            return
        x, y = 20, 115
        sec = player.secondary
        name = type(sec).__name__
        cd = getattr(sec, 'cooldown_timer', 0)
        max_cd = getattr(sec, 'cooldown_max', 1)
        ratio = 1.0 - min(1, cd / max_cd) if max_cd > 0 else 1.0
        color = (0, 255, 150) if ratio >= 1.0 else (80, 120, 100)
        pygame.draw.rect(surface, (20, 40, 30), (x, y, 100, 12))
        pygame.draw.rect(surface, color, (x, y, int(100 * ratio), 12))
        pygame.draw.rect(surface, (100, 200, 150), (x, y, 100, 12), 1)
        txt = self.font_small.render(f"[Q] {name}", True, (150, 255, 180))
        surface.blit(txt, (x, y - 14))

    def _draw_minimap(self, surface, player):
        mm_x = self.sw - 120
        mm_y = self.sh - 120
        mm_w = 100
        mm_h = 100
        bg = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        surface.blit(bg, (mm_x, mm_y))
        pygame.draw.rect(surface, (100, 100, 100), (mm_x, mm_y, mm_w, mm_h), 1)

        arena_w = getattr(player, 'arena_w', 2000)
        arena_h = getattr(player, 'arena_h', 2000)
        px = mm_x + int(player.x / arena_w * mm_w)
        py = mm_y + int(player.y / arena_h * mm_h)
        pygame.draw.circle(surface, (0, 255, 0), (px, py), 3)

        if hasattr(player, 'enemies_ref'):
            for e in player.enemies_ref:
                ex = mm_x + int(e.x / arena_w * mm_w)
                ey = mm_y + int(e.y / arena_h * mm_h)
                pygame.draw.circle(surface, (255, 50, 50), (ex, ey), 2)

        txt = self.font_small.render("MAP", True, (150, 150, 150))
        surface.blit(txt, (mm_x + 38, mm_y - 14))

    def _draw_kill_feed(self, surface):
        x = self.sw - 200
        y = 80
        for i, (msg, timer) in enumerate(zip(self.kill_feed, self.kill_feed_timer)):
            alpha = min(255, int(timer * 255))
            s = self.font_small.render(msg, True, (255, 180, 180))
            s.set_alpha(alpha)
            surface.blit(s, (x, y + i * 18))

    def _draw_boss_bar(self, surface, boss):
        bw = 400
        bh = 30
        bx = self.sw // 2 - bw // 2
        by = self.sh - 60
        pygame.draw.rect(surface, (60, 0, 0), (bx, by, bw, bh))
        ratio = max(0, boss.hp / boss.max_hp)
        phase = getattr(boss, 'phase', 1)
        colors = [(200, 0, 0), (200, 100, 0), (200, 200, 0)]
        color = colors[min(phase - 1, 2)]
        pygame.draw.rect(surface, color, (bx, by, int(bw * ratio), bh))
        pygame.draw.rect(surface, (255, 100, 100), (bx, by, bw, bh), 2)
        name = getattr(boss, 'name', 'BOSS')
        txt = self.font_med.render(f"{name}  Phase {phase}", True, (255, 255, 255))
        surface.blit(txt, (bx + bw // 2 - txt.get_width() // 2, by + 6))

        # Phase markers
        for i in range(1, 3):
            mx = bx + int(bw * (i / 3))
            pygame.draw.line(surface, (255, 255, 255), (mx, by), (mx, by + bh), 2)