import pygame
import math
from constants import *

class HUD:
    def __init__(self):
        self.font_lg = pygame.font.SysFont('arial', 28, bold=True)
        self.font_md = pygame.font.SysFont('arial', 20)
        self.font_sm = pygame.font.SysFont('arial', 15)
        self.kill_feed = []  # [(text, timer)]
        self.kill_feed_duration = 3.0
        self.combo_display_timer = 0.0
        self.boss_hp_bar = None  # (name, current, maximum)
        self.minimap_surface = None

    def add_kill(self, text):
        self.kill_feed.insert(0, [text, self.kill_feed_duration])
        if len(self.kill_feed) > 5:
            self.kill_feed.pop()

    def set_boss(self, name, current, maximum):
        self.boss_hp_bar = (name, current, maximum)

    def clear_boss(self):
        self.boss_hp_bar = None

    def update(self, dt):
        self.kill_feed = [[t, timer - dt] for t, timer in self.kill_feed if timer - dt > 0]
        if self.combo_display_timer > 0:
            self.combo_display_timer -= dt

    def _draw_bar(self, surface, x, y, w, h, value, maximum, color, bg=(40,40,40), border=(200,200,200)):
        pygame.draw.rect(surface, bg, (x, y, w, h))
        if maximum > 0:
            fill = int(w * max(0, value) / maximum)
            pygame.draw.rect(surface, color, (x, y, fill, h))
        pygame.draw.rect(surface, border, (x, y, w, h), 2)

    def draw(self, surface, player, wave, score, coins):
        sw, sh = SCREEN_W, SCREEN_H

        # HP Bar
        hp_color = (220, 50, 50) if player.hp / player.max_hp < 0.3 else (50, 200, 80)
        self._draw_bar(surface, 20, 20, 200, 22, player.hp, player.max_hp, hp_color)
        hp_txt = self.font_sm.render(f'HP {int(player.hp)}/{player.max_hp}', True, (255,255,255))
        surface.blit(hp_txt, (24, 23))

        # Dash cooldown
        dash_pct = 1.0 - min(1.0, player.dash_cooldown_timer / player.dash_cooldown)
        dash_color = (80, 180, 255) if dash_pct >= 1.0 else (100, 100, 180)
        self._draw_bar(surface, 20, 50, 200, 14, dash_pct, 1.0, dash_color)
        dash_lbl = self.font_sm.render('DASH', True, (200,220,255))
        surface.blit(dash_lbl, (24, 51))

        # Weapon info
        if player.current_weapon:
            wname = player.current_weapon.name
            ammo = player.current_weapon.ammo
            max_ammo = player.current_weapon.max_ammo
            reloading = getattr(player.current_weapon, 'reloading', False)
            wtext = f'{wname}  {ammo}/{max_ammo}'
            if reloading:
                wtext += '  [RELOADING]'
            wtxt = self.font_md.render(wtext, True, (255, 220, 100))
            surface.blit(wtxt, (20, 72))

        # Secondary ability
        if player.secondary:
            sec = player.secondary
            cd = getattr(sec, 'cooldown_timer', 0)
            cd_max = getattr(sec, 'cooldown', 1)
            sec_pct = 1.0 - min(1.0, cd / cd_max)
            sec_color = (255, 180, 50) if sec_pct >= 1.0 else (150, 100, 30)
            self._draw_bar(surface, 20, 96, 200, 14, sec_pct, 1.0, sec_color)
            sname = getattr(sec, 'name', 'SECONDARY')
            stxt = self.font_sm.render(sname, True, (255, 200, 100))
            surface.blit(stxt, (24, 97))

        # Wave counter
        wave_txt = self.font_lg.render(f'WAVE {wave}', True, (255, 255, 255))
        surface.blit(wave_txt, (sw//2 - wave_txt.get_width()//2, 12))

        # Score
        score_txt = self.font_md.render(f'SCORE: {score}', True, (255, 230, 80))
        surface.blit(score_txt, (sw - score_txt.get_width() - 20, 20))

        # Coins
        coin_txt = self.font_md.render(f'COINS: {coins}', True, (255, 200, 0))
        surface.blit(coin_txt, (sw - coin_txt.get_width() - 20, 46))

        # Combo
        combo = getattr(player, 'combo', 0)
        if combo > 1:
            alpha = min(255, int(255 * self.combo_display_timer / 2.0))
            combo_txt = self.font_lg.render(f'x{combo} COMBO!', True, (255, 100, 0))
            combo_txt.set_alpha(alpha)
            surface.blit(combo_txt, (sw//2 - combo_txt.get_width()//2, 50))

        # Kill feed
        for i, (text, timer) in enumerate(self.kill_feed):
            alpha = min(255, int(255 * min(1.0, timer)))
            kf_txt = self.font_sm.render(text, True, (255, 150, 150))
            kf_txt.set_alpha(alpha)
            surface.blit(kf_txt, (sw - kf_txt.get_width() - 20, 80 + i * 20))

        # Boss HP bar
        if self.boss_hp_bar:
            bname, bcur, bmax = self.boss_hp_bar
            bw = 400
            bx = sw//2 - bw//2
            by = sh - 60
            self._draw_bar(surface, bx, by, bw, 26, bcur, bmax, (200, 30, 180),
                           bg=(20,10,20), border=(255,100,255))
            bnm = self.font_md.render(bname, True, (255, 100, 255))
            surface.blit(bnm, (bx + bw//2 - bnm.get_width()//2, by + 4))

        # Minimap
        self._draw_minimap(surface, player)

    def _draw_minimap(self, surface, player):
        from arena import TILE_SIZE
        mm_x, mm_y = SCREEN_W - 140, SCREEN_H - 140
        mm_w, mm_h = 120, 120
        mm_surf = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        mm_surf.fill((0, 0, 0, 120))

        arena = getattr(player, '_arena_ref', None)
        if arena:
            scale_x = mm_w / arena.pixel_width
            scale_y = mm_h / arena.pixel_height
            for r in arena.floor_rects:
                rx = int(r.x * scale_x)
                ry = int(r.y * scale_y)
                rw = max(1, int(TILE_SIZE * scale_x))
                rh = max(1, int(TILE_SIZE * scale_y))
                pygame.draw.rect(mm_surf, (80, 75, 70), (rx, ry, rw, rh))
            for h in arena.hazards:
                hx = int(h.rect.x * scale_x)
                hy = int(h.rect.y * scale_y)
                pygame.draw.rect(mm_surf, (200, 80, 0), (hx, hy, 3, 3))

        # Player dot
        px = int(player.rect.centerx * (mm_w / max(1, getattr(getattr(player, '_arena_ref', None), 'pixel_width', SCREEN_W))))
        py = int(player.rect.centery * (mm_h / max(1, getattr(getattr(player, '_arena_ref', None), 'pixel_height', SCREEN_H))))
        px = max(2, min(mm_w-2, px))
        py = max(2, min(mm_h-2, py))
        pygame.draw.circle(mm_surf, (0, 255, 100), (px, py), 3)
        pygame.draw.rect(mm_surf, (180, 180, 180), (0, 0, mm_w, mm_h), 1)
        surface.blit(mm_surf, (mm_x, mm_y))
        lbl = pygame.font.SysFont('arial', 12).render('MAP', True, (200,200,200))
        surface.blit(lbl, (mm_x + mm_w//2 - lbl.get_width()//2, mm_y - 14))