import pygame, math, random
from settings import *
from src.utils import angle_to, distance
from src.particles import ParticleSystem

class Boss:
    def __init__(self, btype, x, y, particles, wave):
        self.btype = btype
        self.x, self.y = float(x), float(y)
        self.particles = particles
        self.wave = wave
        self.phase = 1
        self.alive = True
        self.vx = self.vy = 0.0
        self.anim_t = 0.0
        self.flash_t = 0.0
        self.attack_cd = 0.0
        self.move_cd = 0.0
        self.move_target = (x, y)
        self.vulnerable = False
        self.vuln_timer = 0.0
        self.phase_transition = False
        self.transition_timer = 0.0
        self.death_done = False
        self.death_timer = 0.0
        self.projectiles = []
        self.summons = []
        self._setup()

    def _setup(self):
        configs = {
            'guardian': {'hp':800,  'size':56, 'col':(120,60,200),  'name':'THE GUARDIAN'},
            'inferno':  {'hp':1000, 'size':64, 'col':(255,100,20),  'name':'INFERNO KING'},
            'void':     {'hp':1200, 'size':72, 'col':(40,20,80),    'name':'VOID HERALD'},
        }
        c = configs[self.btype]
        self.hp = c['hp']
        self.max_hp = c['hp']
        self.size = c['size']
        self.col = c['col']
        self.name = c['name']
        self.phase2_hp = c['hp'] * 0.66
        self.phase3_hp = c['hp'] * 0.33
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def get_center(self):
        return (self.x + self.size/2, self.y + self.size/2)

    def take_damage(self, amt):
        if not self.vulnerable and not self.phase_transition:
            return 0
        self.hp -= amt
        self.flash_t = 0.08
        if self.hp <= 0:
            self.hp = 0
            if not self.death_done:
                self.alive = False
                self.death_timer = 2.0
        return amt

    def check_phase(self):
        if self.phase == 1 and self.hp <= self.phase2_hp:
            self.phase = 2
            self.phase_transition = True
            self.transition_timer = 2.0
            self.vulnerable = False
            return True
        if self.phase == 2 and self.hp <= self.phase3_hp:
            self.phase = 3
            self.phase_transition = True
            self.transition_timer = 2.0
            self.vulnerable = False
            return True
        return False

    def update(self, dt, player, arena):
        self.anim_t += dt
        if self.flash_t > 0: self.flash_t -= dt

        if self.phase_transition:
            self.transition_timer -= dt
            self._spawn_transition_particles()
            if self.transition_timer <= 0:
                self.phase_transition = False
                self.vulnerable = True
                self.vuln_timer = 5.0
            return

        if self.vuln_timer > 0:
            self.vuln_timer -= dt
            if self.vuln_timer <= 0:
                self.vulnerable = False

        self.attack_cd -= dt
        self.move_cd -= dt

        px, py = player.get_center()
        bx, by = self.get_center()

        if self.move_cd <= 0:
            self.move_cd = random.uniform(1.5, 3.0)
            if self.btype == 'guardian':
                self.move_target = (px + random.uniform(-100,100), py + random.uniform(-100,100))
            elif self.btype == 'inferno':
                ang = random.uniform(0, math.pi*2)
                r = random.uniform(100, 250)
                self.move_target = (px + math.cos(ang)*r, py + math.sin(ang)*r)
            elif self.btype == 'void':
                self.move_target = (px, py)

        # move toward target
        tx, ty = self.move_target
        dx, dy = tx - self.x, ty - self.y
        d = max(1, math.sqrt(dx*dx+dy*dy))
        spd = 80 + self.phase * 30
        self.vx = (dx/d) * spd
        self.vy = (dy/d) * spd

        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt
        if arena and arena.is_walkable_rect(pygame.Rect(nx, self.y, self.size, self.size)):
            self.x = nx
        if arena and arena.is_walkable_rect(pygame.Rect(self.x, ny, self.size, self.size)):
            self.y = ny

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.attack_cd <= 0:
            self._attack(player)
            self.attack_cd = max(0.8, 2.5 - self.phase * 0.5)

        # update projectiles
        for p in self.projectiles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.projectiles = [p for p in self.projectiles if p['life'] > 0]

        self.check_phase()

    def _spawn_transition_particles(self):
        cx, cy = self.get_center()
        for _ in range(3):
            ang = random.uniform(0, math.pi*2)
            spd = random.uniform(80, 200)
            self.particles.emit(cx, cy, color=self.col,
                vx=math.cos(ang)*spd, vy=math.sin(ang)*spd,
                life=random.uniform(0.5, 1.2), size=random.randint(4, 10))

    def _attack(self, player):
        cx, cy = self.get_center()
        px, py = player.get_center()
        ang = angle_to(cx, cy, px, py)

        if self.btype == 'guardian':
            if self.phase == 1:
                self._shoot_spread(cx, cy, ang, 3, 0.3)
            elif self.phase == 2:
                self._shoot_spread(cx, cy, ang, 5, 0.25)
                self.vulnerable = True; self.vuln_timer = 2.0
            else:
                self._shoot_circle(cx, cy, 8)
                self.vulnerable = True; self.vuln_timer = 1.5

        elif self.btype == 'inferno':
            if self.phase == 1:
                self._shoot_spiral(cx, cy, 4)
            elif self.phase == 2:
                self._shoot_spiral(cx, cy, 8)
                self.vulnerable = True; self.vuln_timer = 2.0
            else:
                self._shoot_spiral(cx, cy, 12)
                self._shoot_spread(cx, cy, ang, 3, 0.4)
                self.vulnerable = True; self.vuln_timer = 1.5

        elif self.btype == 'void':
            if self.phase == 1:
                self._shoot_spread(cx, cy, ang, 5, 0.2)
            elif self.phase == 2:
                self._shoot_circle(cx, cy, 6)
                self._shoot_spread(cx, cy, ang, 3, 0.3)
                self.vulnerable = True; self.vuln_timer = 2.0
            else
# filename: src/hud.py
```python
import pygame
import math
import collections
from settings import *

class KillFeed:
    def __init__(self):
        self.entries = collections.deque(maxlen=5)
        self.font = None

    def add(self, text, color=(255,80,80)):
        self.entries.append({'text': text, 'color': color, 'timer': 3.0, 'alpha': 255})

    def update(self, dt):
        for e in self.entries:
            e['timer'] -= dt
            if e['timer'] < 0.5:
                e['alpha'] = max(0, int(e['timer'] / 0.5 * 255))

    def draw(self, surf, font):
        x = SCREEN_W - 10
        y = 10
        for e in list(self.entries):
            if e['timer'] <= 0:
                continue
            txt = font.render(e['text'], True, e['color'])
            txt.set_alpha(e['alpha'])
            surf.blit(txt, (x - txt.get_width(), y))
            y += 22


class FloatingNumber:
    def __init__(self, x, y, value, color=(255,255,80), crit=False):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.crit = crit
        self.timer = 1.2
        self.vy = -60

    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.95
        self.timer -= dt

    def draw(self, surf, font, camera):
        if self.timer <= 0:
            return
        alpha = min(255, int(self.timer / 1.2 * 255))
        sx, sy = camera.world_to_screen(self.x, self.y)
        text = f"{'CRIT! ' if self.crit else ''}{int(self.value)}"
        size = 28 if self.crit else 20
        txt = font.render(text, True, self.color)
        txt.set_alpha(alpha)
        surf.blit(txt, (sx - txt.get_width()//2, sy))


class HUD:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.kill_feed = KillFeed()
        self.floating_numbers = []
        self.combo = 0
        self.combo_timer = 0
        self.combo_max_time = 3.0
        self._init_fonts()
        self.minimap_surf = pygame.Surface((160, 120), pygame.SRCALPHA)

    def _init_fonts(self):
        pygame.font.init()
        try:
            self.font_sm = pygame.font.SysFont('monospace', 16, bold=True)
            self.font_md = pygame.font.SysFont('monospace', 22, bold=True)
            self.font_lg = pygame.font.SysFont('monospace', 32, bold=True)
            self.font_crit = pygame.font.SysFont('monospace', 28, bold=True)
        except:
            self.font_sm = pygame.font.Font(None, 18)
            self.font_md = pygame.font.Font(None, 24)
            self.font_lg = pygame.font.Font(None, 34)
            self.font_crit = pygame.font.Font(None, 30)

    def add_kill(self, enemy_name):
        self.kill_feed.add(f"KILLED {enemy_name.upper()}")
        self.combo += 1
        self.combo_timer = self.combo_max_time

    def add_damage(self, x, y, value, crit=False):
        color = (255, 50, 50) if crit else (255, 220, 80)
        self.floating_numbers.append(FloatingNumber(x, y, value, color, crit))

    def update(self, dt):
        self.kill_feed.update(dt)
        self.floating_numbers = [fn for fn in self.floating_numbers if fn.timer > 0]
        for fn in self.floating_numbers:
            fn.update(dt)
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

    def draw_bar(self, surf, x, y, w, h, val, max_val, fg, bg=(40,40,40), border=(200,200,200)):
        pygame.draw.rect(surf, bg, (x, y, w, h))
        fill = int(w * max(0, val) / max(1, max_val))
        if fill > 0:
            pygame.draw.rect(surf, fg, (x, y, fill, h))
        pygame.draw.rect(surf, border, (x, y, w, h), 2)

    def draw(self, surf, player, wave, score, camera, tilemap=None):
        # HP bar
        hp_color = (80, 220, 80)
        if player.hp / player.max_hp < 0.3:
            hp_color = (220, 60, 60)
        elif player.hp / player.max_hp < 0.6:
            hp_color = (220, 180, 60)
        self.draw_bar(surf, 10, self.screen_h - 40, 200, 24, player.hp, player.max_hp, hp_color)
        hp_txt = self.font_sm.render(f"HP {int(player.hp)}/{int(player.max_hp)}", True, (255,255,255))
        surf.blit(hp_txt, (15, self.screen_h - 37))

        # Dash cooldown
        dash_cd = getattr(player, 'dash_cooldown', 0)
        dash_max = getattr(player, 'dash_cooldown_max', 1.0)
        dash_ready = dash_cd <= 0
        dash_col = (80,200,255) if dash_ready else (100,100,150)
        self.draw_bar(surf, 10, self.screen_h - 68, 200, 16, dash_max - dash_cd, dash_max, dash_col)
        dash_txt = self.font_sm.render("DASH" if dash_ready else f"DASH {dash_cd:.1f}s", True, (255,255,255))
        surf.blit(dash_txt, (15, self.screen_h - 66))

        # Weapon / ammo
        weapon = getattr(player, 'current_weapon', None)
        if weapon:
            wname = type(weapon).__name__.replace('Weapon','').upper()
            ammo = getattr(weapon, 'ammo', -1)
            max_ammo = getattr(weapon, 'max_ammo', -1)
            ammo_str = f"{ammo}/{max_ammo}" if ammo >= 0 else "INF"
            wt = self.font_md.render(f"{wname}  {ammo_str}", True, (255,200,100))
            surf.blit(wt, (10, self.screen_h - 100))

        # Secondary ability
        ability = getattr(player, 'current_ability', None)
        if ability:
            aname = type(ability).__name__.replace('Ability','').upper()
            acd = getattr(ability, 'cooldown_timer', 0)
            amax = getattr(ability, 'cooldown', 1)
            acol = (200,100,255) if acd <= 0 else (100,80,120)
            self.draw_bar(surf, 10, self.screen_h - 125, 200, 14, amax - acd, amax, acol)
            at = self.font_sm.render(aname, True, (220,180,255))
            surf.blit(at, (15, self.screen_h - 123))

        # Wave / score / coins
        wave_txt = self.font_md.render(f"WAVE {wave}", True, (255,255,100))
        surf.blit(wave_txt, (self.screen_w//2 - wave_txt.get_width()//2, 10))
        score_txt = self.font_sm.render(f"SCORE: {score}", True, (200,200,200))
        surf.blit(score_txt, (self.screen_w//2 - score_txt.get_width()//2, 38))
        coins = getattr(player, 'coins', 0)
        coin_txt = self.font_sm.render(f"COINS: {coins}", True, (255,220,60))
        surf.blit(coin_txt, (self.screen_w//2 - coin_txt.get_width()//2, 58))

        # Combo
        if self.combo > 1:
            alpha = min(255, int(self.combo_timer / self.combo_max_time * 255))
            combo_col = (255, min(255, 50 + self.combo*20), 50)
            ct = self.font_lg.render(f"x{self.combo} COMBO!", True, combo_col)
            ct.set_alpha(alpha)
            surf.blit(ct, (self.screen_w//2 - ct.get_width()//2, 90))

        # Kill feed
        self.kill_feed.draw(surf, self.font_sm)

        # Floating numbers
        for fn in self.floating_numbers:
            fn.draw(surf, self.font_sm, camera)

        # Minimap
        if tilemap:
            self._draw_minimap(surf, tilemap, player, camera)

    def draw_boss_bar(self, surf, boss):
        bname = type(boss).__name__.upper()
        phase = getattr(boss, 'phase', 1)
        bar_w = 600
        bar_h = 28
        x = self.screen_w//2 - bar_w//2
        y = 10
        # background
        pygame.draw.rect(surf, (20,10,10), (x-2, y-2, bar_w+4, bar_h+4))
        self.draw_bar(surf, x, y, bar_w, bar_h, boss.hp, boss.max_hp, (220,40,40), (60,20,20), (255,100,100))
        label = self.font_md.render(f"{bname}  PHASE {phase}  {int(boss.hp)}/{int(boss.max_hp)}", True, (255,150,150))
        surf.blit(label, (x + bar_w//2 - label.get_width()//2, y + 4))

    def _draw_minimap(self, surf, tilemap, player, camera):
        mm_w, mm_h = 160, 120
        mm_x = self.screen_w - mm_w - 10
        mm_y = 10
        self.minimap_surf.fill((0,0,0,180))
        cols = getattr(tilemap, 'cols', 50)
        rows = getattr(tilemap, 'rows', 38)
        cell_w = mm_w / cols
        cell_h = mm_h / rows
        for r in range(rows):
            for c in range(cols):
                tile = tilemap.get_tile(c, r)
                if tile is None:
                    continue
                solid = getattr(tile, 'solid', False)
                color = (60,60,60,200) if solid else (120,120,140,180)
                pygame.draw.rect(self.minimap_surf, color,
                    (int(c*cell_w), int(r*cell_h), max(1,int(cell_w)), max(1,int(cell_h))))
        # player dot
        px = player.x / (cols * TILE_SIZE * SCALE)
        py = player.y / (rows * TILE_SIZE * SCALE)
        pdx = int(px * mm_w)
        pdy = int(py * mm_h)
        pygame.draw.circle(self.minimap_surf, (80,220,80), (pdx, pdy), 3)
        # border
        pygame.draw.rect(self.minimap_surf, (200,200,200,255), (0,0,mm_w,mm_h), 2)
        surf.blit(self.minimap_surf, (mm_x, mm_y))