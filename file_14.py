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
# filename: hud.py
```python
import pygame
import math
from settings import *

class HUD:
    def __init__(self, game):
        self.game = game
        self.kill_feed = []
        self.damage_numbers = []
        self.combo_display_timer = 0
        self.wave_transition_timer = 0
        self.wave_transition_text = ""
        self.boss_hp_bar_alpha = 0
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        self.fonts['small'] = pygame.font.SysFont('monospace', 12, bold=True)
        self.fonts['medium'] = pygame.font.SysFont('monospace', 18, bold=True)
        self.fonts['large'] = pygame.font.SysFont('monospace', 28, bold=True)
        self.fonts['huge'] = pygame.font.SysFont('monospace', 48, bold=True)
        self.fonts['tiny'] = pygame.font.SysFont('monospace', 10, bold=True)

    def add_damage_number(self, x, y, value, color=(255, 255, 100), crit=False):
        self.damage_numbers.append({
            'x': x, 'y': y,
            'value': value,
            'color': color,
            'crit': crit,
            'timer': 1.2,
            'vy': -80,
            'alpha': 255
        })

    def add_kill_feed(self, text, color=(255, 100, 100)):
        self.kill_feed.append({'text': text, 'color': color, 'timer': 3.0})
        if len(self.kill_feed) > 5:
            self.kill_feed.pop(0)

    def show_wave_transition(self, text):
        self.wave_transition_text = text
        self.wave_transition_timer = 3.0

    def update(self, dt):
        self.damage_numbers = [d for d in self.damage_numbers if d['timer'] > 0]
        for d in self.damage_numbers:
            d['timer'] -= dt
            d['y'] += d['vy'] * dt
            d['vy'] *= 0.95
            d['alpha'] = max(0, int(255 * (d['timer'] / 1.2)))

        self.kill_feed = [k for k in self.kill_feed if k['timer'] > 0]
        for k in self.kill_feed:
            k['timer'] -= dt

        if self.combo_display_timer > 0:
            self.combo_display_timer -= dt

        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= dt

        boss = getattr(self.game, 'current_boss', None)
        if boss and boss.alive:
            self.boss_hp_bar_alpha = min(255, self.boss_hp_bar_alpha + 300 * dt)
        else:
            self.boss_hp_bar_alpha = max(0, self.boss_hp_bar_alpha - 200 * dt)

    def draw(self, surface):
        player = self.game.player
        self._draw_hp_bar(surface, player)
        self._draw_dash_cooldown(surface, player)
        self._draw_weapon_info(surface, player)
        self._draw_wave_score(surface)
        self._draw_combo(surface, player)
        self._draw_minimap(surface)
        self._draw_kill_feed(surface)
        self._draw_damage_numbers(surface)
        if self.boss_hp_bar_alpha > 0:
            self._draw_boss_hp_bar(surface)
        if self.wave_transition_timer > 0:
            self._draw_wave_transition(surface)
        self._draw_coins(surface)

    def _draw_hp_bar(self, surface, player):
        x, y = 20, SCREEN_H - 60
        w, h = 200, 20
        ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(surface, (60, 0, 0), (x, y, w, h))
        color = (200, 50, 50) if ratio > 0.3 else (255, 50, 50)
        if ratio > 0.6:
            color = (50, 200, 50)
        elif ratio > 0.3:
            color = (200, 200, 50)
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2)
        txt = self.fonts['small'].render(f'HP {int(player.hp)}/{int(player.max_hp)}', True, (255, 255, 255))
        surface.blit(txt, (x + 4, y + 3))

        # Armor bar if any
        if hasattr(player, 'armor') and player.armor > 0:
            ar = self.fonts['tiny'].render(f'ARM:{int(player.armor)}', True, (100, 200, 255))
            surface.blit(ar, (x + 4, y - 14))

    def _draw_dash_cooldown(self, surface, player):
        x, y = 20, SCREEN_H - 30
        w, h = 80, 12
        cd_ratio = 1.0 - min(1.0, player.dash_cooldown_timer / player.dash_cooldown)
        pygame.draw.rect(surface, (20, 20, 60), (x, y, w, h))
        pygame.draw.rect(surface, (80, 80, 255), (x, y, int(w * cd_ratio), h))
        pygame.draw.rect(surface, (150, 150, 255), (x, y, w, h), 1)
        txt = self.fonts['tiny'].render('DASH', True, (200, 200, 255))
        surface.blit(txt, (x + w + 4, y))

    def _draw_weapon_info(self, surface, player):
        x, y = 240, SCREEN_H - 60
        weapon = player.current_weapon
        if weapon is None:
            return
        name = weapon.__class__.__name__.upper()
        ammo_str = f"{weapon.current_ammo}/{weapon.max_ammo}" if hasattr(weapon, 'current_ammo') else "INF"
        color_map = {
            'PISTOL': (200, 200, 200),
            'SHOTGUN': (255, 150, 50),
            'ROCKETLAUNCHER': (255, 80, 80),
            'RAILGUN': (80, 200, 255),
            'CHAINLIGHTNING': (255, 255, 80),
            'BOOMERANG': (100, 255, 100),
            'FLAMETHROWER': (255, 120, 30),
            'CROSSBOW': (180, 120, 255),
        }
        wcolor = color_map.get(name, (200, 200, 200))
        wtxt = self.fonts['medium'].render(name, True, wcolor)
        surface.blit(wtxt, (x, y))
        ammo_color = (255, 80, 80) if weapon.current_ammo <= 3 else (200, 200, 200)
        atxt = self.fonts['small'].render(f'AMMO: {ammo_str}', True, ammo_color)
        surface.blit(atxt, (x, y + 20))

        # Reload bar
        if hasattr(weapon, 'reload_timer') and weapon.reload_timer > 0:
            rw = 120
            ratio = 1.0 - (weapon.reload_timer / weapon.reload_time)
            pygame.draw.rect(surface, (40, 40, 40), (x, y + 38, rw, 8))
            pygame.draw.rect(surface, (255, 200, 50), (x, y + 38, int(rw * ratio), 8))
            rtxt = self.fonts['tiny'].render('RELOADING', True, (255, 200, 50))
            surface.blit(rtxt, (x + rw + 4, y + 36))

        # Weapon slot indicators
        for i, w in enumerate(player.weapons):
            slot_x = x + i * 30
            slot_y = y + 50
            active = (i == player.weapon_index)
            bc = wcolor if active else (80, 80, 80)
            pygame.draw.rect(surface, (20, 20, 20), (slot_x, slot_y, 24, 16))
            pygame.draw.rect(surface, bc, (slot_x, slot_y, 24, 16), 2 if active else 1)
            sn = self.fonts['tiny'].render(str(i + 1), True, bc)
            surface.blit(sn, (slot_x + 8, slot_y + 2))

    def _draw_wave_score(self, surface):
        wave_txt = self.fonts['medium'].render(f'WAVE {self.game.wave}', True, (255, 220, 100))
        surface.blit(wave_txt, (SCREEN_W // 2 - wave_txt.get_width() // 2, 10))
        score_txt = self.fonts['small'].render(f'SCORE: {self.game.score:,}', True, (200, 200, 255))
        surface.blit(score_txt, (SCREEN_W - score_txt.get_width() - 20, 10))
        enemies_left = len([e for e in self.game.enemies if e.alive])
        el_txt = self.fonts['small'].render(f'ENEMIES: {enemies_left}', True, (255, 150, 150))
        surface.blit(el_txt, (SCREEN_W - el_txt.get_width() - 20, 30))

    def _draw_combo(self, surface, player):
        if player.combo_count >= 3:
            scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)
            combo_str = f'x{player.combo_count} COMBO!'
            size = int(24 * scale)
            try:
                f = pygame.font.SysFont('monospace', size, bold=True)
            except:
                f = self.fonts['large']
            colors = [(255, 255, 100), (255, 150, 50), (255, 80, 80), (200, 50, 255)]
            c_idx = (player.combo_count // 5) % len(colors)
            ctxt = f.render(combo_str, True, colors[c_idx])
            surface.blit(ctxt, (SCREEN_W // 2 - ctxt.get_width() // 2, SCREEN_H - 120))

    def _draw_minimap(self, surface):
        mm_w, mm_h = 150, 100
        mm_x = SCREEN_W - mm_w - 10
        mm_y = SCREEN_H - mm_h - 10
        mm_surf = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        mm_surf.fill((0, 0, 0, 160))

        arena_w = self.game.arena.width * TILE_SIZE
        arena_h = self.game.arena.height * TILE_SIZE
        sx = mm_w / arena_w
        sy = mm_h / arena_h

        # Draw tiles
        tilemap = self.game.arena.tilemap
        for ty in range(0, tilemap.height, 3):
            for tx in range(0, tilemap.width, 3):
                tile = tilemap.get_tile(tx, ty)
                if tile and tile.get('wall'):
                    px = int(tx * TILE_SIZE * sx)
                    py = int(ty * TILE_SIZE * sy)
                    pygame.draw.rect(mm_surf, (100, 100, 120), (px, py, max(1, int(TILE_SIZE * sx * 3)), max(1, int(TILE_SIZE * sy * 3))))

        # Enemies
        for e in self.game.enemies:
            if e.alive:
                ex = int(e.x * sx)
                ey = int(e.y * sy)
                pygame.draw.circle(mm_surf, (255, 80, 80), (ex, ey), 2)

        # Player
        px = int(self.game.player.x * sx)
        py = int(self.game.player.y * sy)
        pygame.draw.circle(mm_surf, (100, 255, 100), (px, py), 3)

        # Boss
        boss = getattr(self.game, 'current_boss', None)
        if boss and boss.alive:
            bx = int(boss.x * sx)
            by = int(boss.y * sy)
            pygame.draw.circle(mm_surf, (255, 50, 255), (bx, by), 4)

        pygame.draw.rect(mm_surf, (200, 200, 200, 200), (0, 0, mm_w, mm_h), 1)
        surface.blit(mm_surf, (mm_x, mm_y))

    def _draw_kill_feed(self, surface):
        x = SCREEN_W - 220
        y = 60
        for kf in reversed(self.kill_feed):
            alpha = min(255, int(kf['timer'] / 3.0 * 255))
            txt = self.fonts['tiny'].render(kf['text'], True, kf['color'])
            txt.set_alpha(alpha)
            surface.blit(txt, (x, y))
            y += 14

    def _draw_damage_numbers(self, surface):
        cam = self.game.camera
        for d in self.damage_numbers:
            sx, sy = cam.world_to_screen(d['x'], d['y'])
            if 0 <= sx <= SCREEN_W and 0 <= sy <= SCREEN_H:
                size = 20 if d['crit'] else 14
                try:
                    f = pygame.font.SysFont('monospace', size, bold=True)
                except:
                    f = self.fonts['small']
                val_str = str(int(d['value']))
                if d['crit']:
                    val_str = 'CRIT! ' + val_str
                txt = f.render(val_str, True, d['color'])
                txt.set_alpha(d['alpha'])
                surface.blit(txt, (sx - txt.get_width() // 2, int(sy)))

    def _draw_boss_hp_bar(self, surface):
        boss = getattr(self.game, 'current_boss', None)
        if not boss:
            return
        bw, bh = 400, 24
        bx = SCREEN_W // 2 - bw // 2
        by = 50
        surf = pygame.Surface((bw, bh + 30), pygame.SRCALPHA)

        name_txt = self.fonts['medium'].render(boss.name.upper(), True, (255, 200, 255))
        surf.blit(name_txt, (bw // 2 - name_txt.get_width() // 2, 0))

        ratio = max(0, boss.hp / boss.max_hp)
        pygame.draw.rect(surf, (60, 0, 60), (0, 22, bw, bh))
        bar_color = (200, 50, 200)
        if ratio > 0.6:
            bar_color = (200, 50, 200)
        elif ratio > 0.3:
            bar_color = (255, 100, 50)
        else:
            bar_color = (255, 50, 50)
        pygame.draw.rect(surf, bar_color, (0, 22, int(bw * ratio), bh))

        # Phase markers
        for p in [0.33, 0.66]:
            mx = int(bw * p)
            pygame.draw.line(surf, (255, 255, 255), (mx, 22), (mx, 22 + bh), 2)

        pygame.draw.rect(surf, (200, 150, 200), (0, 22, bw, bh), 2)
        phase_txt = self.fonts['tiny'].render(f'PHASE {boss.phase}', True, (255, 200, 255))
        surf.blit(phase_txt, (4, 26))
        hp_txt = self.fonts['tiny'].render(f'{int(boss.hp)}/{int(boss.max_hp)}', True, (255, 255, 255))
        surf.blit(hp_txt, (bw - hp_txt.get_width() - 4, 26))

        surf.set_alpha(int(self.boss_hp_bar_alpha))
        surface.blit(surf, (bx, by))

    def _draw_wave_transition(self, surface):
        t = self.wave_transition_timer
        alpha = 255
        if t > 2.5:
            alpha = int(255 * (3.0 - t) / 0.5)
        elif t < 0.5:
            alpha = int(255 * t / 0.5)

        surf = pygame.Surface((SCREEN_W, 100), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 120))
        txt = self.fonts['huge'].render(self.wave_transition_text, True, (255, 220, 100))
        surf.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 25))
        surf.set_alpha(alpha)
        surface.blit(surf, (0, SCREEN_H // 2 - 50))

    def _draw_coins(self, surface):
        coins = getattr(self.game.player, 'coins', 0)
        txt = self.fonts['medium'].render(f'${coins}', True, (255, 220, 50))
        surface.blit(txt, (20, SCREEN_H - 90))