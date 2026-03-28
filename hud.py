import pygame
import math


class KillFeedEntry:
    def __init__(self, text, color=(255, 200, 100)):
        self.text = text
        self.color = color
        self.life = 4.0
        self.max_life = 4.0
        self.y_offset = 0.0


class HUD:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.kill_feed = []
        self.combo_display = 0
        self.combo_alpha = 0
        self.boss_visible = False
        self.boss_name = ""
        self.boss_hp = 1.0
        self.boss_hp_target = 1.0
        self.wave_flash = 0.0
        self.wave_flash_text = ""
        self.damage_flash = 0.0

        try:
            self.font_large = pygame.font.Font(None, 42)
            self.font_med = pygame.font.Font(None, 30)
            self.font_small = pygame.font.Font(None, 22)
            self.font_tiny = pygame.font.Font(None, 18)
            self.font_combo = pygame.font.Font(None, 72)
            self.font_boss = pygame.font.Font(None, 36)
        except Exception:
            self.font_large = pygame.font.SysFont('arial', 32)
            self.font_med = pygame.font.SysFont('arial', 24)
            self.font_small = pygame.font.SysFont('arial', 18)
            self.font_tiny = pygame.font.SysFont('arial', 14)
            self.font_combo = pygame.font.SysFont('arial', 56)
            self.font_boss = pygame.font.SysFont('arial', 28)

        self.minimap_surf = None
        self.minimap_scale = 0.08
        self.minimap_update_timer = 0.0

        self.weapon_names = [
            "Pistol", "Shotgun", "Sniper", "Rocket",
            "ChainGun", "Boomerang", "Flamethrow", "Grenade"
        ]
        self.ability_names = [
            "Shield", "TimeSlow", "Turret", "AdrenaLine",
            "BlackHole", "IceWall"
        ]
        self.weapon_icons_color = [
            (200, 200, 255), (255, 150, 50), (100, 255, 100),
            (255, 80, 80), (255, 220, 50), (100, 200, 255),
            (255, 120, 50), (150, 255, 150)
        ]

    def add_kill(self, enemy_name, color=(255, 200, 100)):
        entry = KillFeedEntry(f"Killed {enemy_name}", color)
        self.kill_feed.insert(0, entry)
        if len(self.kill_feed) > 6:
            self.kill_feed.pop()

    def show_wave(self, wave_num):
        self.wave_flash = 3.0
        self.wave_flash_text = f"WAVE {wave_num}"

    def show_damage(self):
        self.damage_flash = 0.4

    def update(self, dt):
        self.kill_feed = [e for e in self.kill_feed if e.life > 0]
        for e in self.kill_feed:
            e.life -= dt

        if self.combo_alpha > 0:
            self.combo_alpha = max(0, self.combo_alpha - dt * 120)

        if self.boss_hp_target != self.boss_hp:
            self.boss_hp += (self.boss_hp_target - self.boss_hp) * min(1, dt * 4)

        if self.wave_flash > 0:
            self.wave_flash -= dt

        if self.damage_flash > 0:
            self.damage_flash -= dt

        self.minimap_update_timer += dt

    def set_combo(self, combo):
        self.combo_display = combo
        if combo > 1:
            self.combo_alpha = 255

    def set_boss(self, name, hp_frac):
        self.boss_visible = True
        self.boss_name = name
        self.boss_hp_target = max(0.0, min(1.0, hp_frac))

    def hide_boss(self):
        self.boss_visible = False

    def _draw_bar(self, surf, x, y, w, h, frac, fg_color, bg_color=(40, 40, 40), border=True):
        pygame.draw.rect(surf, bg_color, (x, y, w, h))
        fill_w = int(w * max(0, min(1, frac)))
        if fill_w > 0:
            pygame.draw.rect(surf, fg_color, (x, y, fill_w, h))
        if border:
            pygame.draw.rect(surf, (200, 200, 200), (x, y, w, h), 1)

    def draw(self, surf, player, wave, score, coins, arena=None):
        self._draw_hp(surf, player)
        self._draw_dash(surf, player)
        self._draw_weapon(surf, player)
        self._draw_wave_score(surf, wave, score, coins)
        self._draw_combo(surf)
        self._draw_kill_feed(surf)
        if self.boss_visible:
            self._draw_boss_bar(surf)
        if self.wave_flash > 0:
            self._draw_wave_flash(surf)
        if self.damage_flash > 0:
            self._draw_damage_flash(surf)
        if arena is not None:
            self._draw_minimap(surf, player, arena)

    def _draw_hp(self, surf, player):
        x, y, w, h = 20, self.screen_h - 70, 220, 22
        max_hp = getattr(player, 'max_hp', 100)
        hp = getattr(player, 'hp', 100)
        frac = hp / max(1, max_hp)

        if frac > 0.6:
            color = (50, 220, 80)
        elif frac > 0.3:
            color = (220, 180, 50)
        else:
            r = int(220 + 35 * math.sin(pygame.time.get_ticks() * 0.01))
            color = (min(255, r), 50, 50)

        pygame.draw.rect(surf, (20, 20, 20), (x - 2, y - 2, w + 4, h + 4))
        self._draw_bar(surf, x, y, w, h, frac, color)

        hp_text = self.font_small.render(f"HP  {int(hp)}/{int(max_hp)}", True, (255, 255, 255))
        surf.blit(hp_text, (x + 4, y + 3))

        label = self.font_tiny.render("HEALTH", True, (180, 180, 180))
        surf.blit(label, (x, y - 16))

        shield = getattr(player, 'shield', 0)
        if shield > 0:
            sx, sy = x, y - 28
            sw = int(w * min(1.0, shield / 100))
            pygame.draw.rect(surf, (20, 20, 60), (sx, sy, w, 10))
            pygame.draw.rect(surf, (80, 150, 255), (sx, sy, sw, 10))
            pygame.draw.rect(surf, (150, 200, 255), (sx, sy, w, 10), 1)
            sl = self.font_tiny.render(f"SHIELD {int(shield)}", True, (150, 200, 255))
            surf.blit(sl, (sx + 2, sy + 1))

    def _draw_dash(self, surf, player):
        x, y = 20, self.screen_h - 40
        dash_cd = getattr(player, 'dash_cooldown', 0)
        max_dash_cd = getattr(player, 'dash_cooldown_max', 1.0)
        frac = 1.0 - (dash_cd / max(0.01, max_dash_cd))

        label = self.font_tiny.render("DASH", True, (180, 180, 180))
        surf.blit(label, (x, y - 2))

        bx = x + 38
        self._draw_bar(surf, bx, y, 100, 14, frac,
                       (100, 200, 255) if frac >= 1.0 else (50, 120, 200))
        if frac >= 1.0:
            ready = self.font_tiny.render("READY", True, (100, 255, 200))
            surf.blit(ready, (bx + 30, y + 1))

    def _draw_weapon(self, surf, player):
        x = self.screen_w - 260
        y = self.screen_h - 130

        pygame.draw.rect(surf, (15, 15, 30), (x - 5, y - 5, 255, 125), border_radius=6)
        pygame.draw.rect(surf, (80, 80, 120), (x - 5, y - 5, 255, 125), 1, border_radius=6)

        current_weapon = getattr(player, 'current_weapon', 0)
        weapons = getattr(player, 'weapons', [])

        wname = self.weapon_names[current_weapon] if current_weapon < len(self.weapon_names) else "Unknown"
        wcolor = self.weapon_icons_color[current_weapon] if current_weapon < len(self.weapon_icons_color) else (200, 200, 200)

        wlabel = self.font_med.render(f"[{current_weapon + 1}] {wname}", True, wcolor)
        surf.blit(wlabel, (x, y))

        if weapons and current_weapon < len(weapons):
            w = weapons[current_weapon]
            ammo = getattr(w, 'ammo', None)
            max_ammo = getattr(w, 'max_ammo', None)
            if ammo is not None and max_ammo is not None:
                ammo_frac = ammo / max(1, max_ammo)
                self._draw_bar(surf, x, y + 28, 160, 12, ammo_frac,
                               (255, 200, 50), border=True)
                atxt = self.font_tiny.render(f"{int(ammo)}/{int(max_ammo)}", True, (220, 220, 150))
                surf.blit(atxt, (x + 165, y + 28))

            fire_timer = getattr(w, 'fire_timer', 0)
            fire_rate = getattr(w, 'fire_rate', 1)
            reload_t = getattr(w, 'reload_timer', 0)
            if reload_t > 0:
                rl = self.font_small.render("RELOADING...", True, (255, 150, 50))
                surf.blit(rl, (x, y + 44))
            else:
                cd_frac = 1.0 - min(1.0, fire_timer / max(0.001, 1.0 / max(0.001, fire_rate)))
                self._draw_bar(surf, x, y + 44, 100, 8, cd_frac, (200, 100, 255))

        ability_idx = getattr(player, 'current_ability', 0)
        aname = self.ability_names[ability_idx] if ability_idx < len(self.ability_names) else "None"
        ability_cd = getattr(player, 'ability_cooldown', 0)
        ability_max_cd = getattr(player, 'ability_cooldown_max', 10.0)
        a_frac = 1.0 - (ability_cd / max(0.01, ability_max_cd))

        alabel = self.font_small.render(f"ABILITY: {aname}", True, (200, 150, 255))
        surf.blit(alabel, (x, y + 60))
        self._draw_bar(surf, x, y + 78, 160, 10, a_frac,
                       (200, 100, 255) if a_frac >= 1.0 else (100, 50, 150))
        if a_frac >= 1.0:
            rdy = self.font_tiny.render("READY [RMB]", True, (200, 150, 255))
            surf.blit(rdy, (x + 165, y + 79))

        for i in range(min(8, len(self.weapon_names))):
            wx = x + i * 30
            wy = y + 96
            is_cur = (i == current_weapon)
            wc = self.weapon_icons_color[i] if i < len(self.weapon_icons_color) else (150, 150, 150)
            if is_cur:
                pygame.draw.rect(surf, wc, (wx, wy, 24, 16), border_radius=3)
                num = self.font_tiny.render(str(i + 1), True, (0, 0, 0))
            else:
                pygame.draw.rect(surf, (40, 40, 60), (wx, wy, 24, 16), border_radius=3)
                pygame.draw.rect(surf, wc, (wx, wy, 24, 16), 1, border_radius=3)
                num = self.font_tiny.render(str(i + 1), True, wc)
            surf.blit(num, (wx + 8, wy + 2))

    def _draw_wave_score(self, surf, wave, score, coins):
        x = self.screen_w // 2
        y = 10

        wave_t = self.font_med.render(f"WAVE {wave}", True, (200, 200, 255))
        surf.blit(wave_t, (x - wave_t.get_width() // 2, y))

        score_t = self.font_small.render(f"SCORE: {score:,}", True, (255,