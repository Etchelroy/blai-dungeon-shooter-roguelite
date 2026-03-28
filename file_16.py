import pygame
import random
from settings import *

UPGRADE_POOL = [
    {'name': 'Swift Boots', 'desc': 'Move 15% faster', 'rarity': 'common', 'color': (180, 180, 180),
     'apply': lambda p: setattr(p, 'speed', p.speed * 1.15)},
    {'name': 'Iron Skin', 'desc': '+25 max HP', 'rarity': 'common', 'color': (180, 180, 180),
     'apply': lambda p: (setattr(p, 'max_hp', p.max_hp + 25), setattr(p, 'hp', min(p.max_hp, p.hp + 25)))},
    {'name': 'Sharp Eye', 'desc': '+20% crit chance', 'rarity': 'uncommon', 'color': (100, 200, 100),
     'apply': lambda p: setattr(p, 'crit_chance', getattr(p, 'crit_chance', 0.05) + 0.20)},
    {'name': 'Hollow Points', 'desc': '+30% damage', 'rarity': 'uncommon', 'color': (100, 200, 100),
     'apply': lambda p: setattr(p, 'damage_mult', getattr(p, 'damage_mult', 1.0) * 1.30)},
    {'name': 'Ghost Step', 'desc': 'Longer i-frames on dash', 'rarity': 'uncommon', 'color': (100, 200, 100),
     'apply': lambda p: setattr(p, 'dash_iframes', getattr(p, 'dash_iframes', 0.15) + 0.1)},
    {'name': 'Inferno', 'desc': 'Bullets set enemies on fire', 'rarity': 'rare', 'color': (80, 120, 255),
     'apply': lambda p: setattr(p, 'fire_ammo', True)},
    {'name': 'Chain Reaction', 'desc': 'Explosions chain to nearby enemies', 'rarity': 'rare', 'color': (80, 120, 255),
     'apply': lambda p: setattr(p, 'chain_explosion', True)},
    {'name': 'Vampirism', 'desc': 'Heal 8% of damage dealt', 'rarity': 'rare', 'color': (80, 120, 255),
     'apply': lambda p: setattr(p, 'lifesteal', getattr(p, 'lifesteal', 0) + 0.08)},
    {'name': 'Overdrive', 'desc': '+50% fire rate, -20% damage', 'rarity': 'rare', 'color': (80, 120, 255),
     'apply': lambda p: _overdrive(p)},
    {'name': 'Phoenix Feather', 'desc': 'Revive once with 50% HP', 'rarity': 'epic', 'color': (200, 50, 255),
     'apply': lambda p: setattr(p, 'revive', True)},
    {'name': 'Bullet Storm', 'desc': '+2 projectiles per shot', 'rarity': 'epic', 'color': (200, 50, 255),
     'apply': lambda p: setattr(p, 'extra_projectiles', getattr(p, 'extra_projectiles', 0) + 2)},
    {'name': 'Time Thief', 'desc': 'Each kill resets dash', 'rarity': 'epic', 'color': (200, 50, 255),
     'apply': lambda p: setattr(p, 'kill_resets_dash', True)},
    {'name': 'Cold Blood', 'desc': '+5% damage per kill stack (max 50%)', 'rarity': 'uncommon', 'color': (100, 200, 100),
     'apply': lambda p: setattr(p, 'kill_stack_damage', True)},
    {'name': 'Fortify', 'desc': 'Blocks next 3 hits', 'rarity': 'rare', 'color': (80, 120, 255),
     'apply': lambda p: setattr(p, 'block_charges', getattr(p, 'block_charges', 0) + 3)},
]

def _overdrive(p):
    setattr(p, 'damage_mult', getattr(p, 'damage_mult', 1.0) * 0.8)
    for w in p.weapons:
        if hasattr(w, 'fire_rate'):
            w.fire_rate = max(0.05, w.fire_rate * 0.5)

RARITY_WEIGHTS = {'common': 50, 'uncommon': 30, 'rare': 15, 'epic': 5}
RARITY_COLORS = {'common': (180, 180, 180), 'uncommon': (100, 200, 100), 'rare': (80, 120, 255), 'epic': (200, 50, 255)}

class UpgradeScreen:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.choices = []
        self.selected = 0
        self.font_huge = pygame.font.SysFont('monospace', 36, bold=True)
        self.font_large = pygame.font.SysFont('monospace', 22, bold=True)
        self.font_med = pygame.font.SysFont('monospace', 15, bold=True)
        self.font_small = pygame.font.SysFont('monospace', 12, bold=True)
        self.anim_timer = 0
        self.card_offsets = [0, 0, 0]

    def open(self):
        self.active = True
        self.choices = self._pick_upgrades(3)
        self.selected = 0
        self.anim_timer = 0
        self.card_offsets = [300, 300, 300]

    def _pick_upgrades(self, count):
        pool = UPGRADE_POOL.copy()
        weights = [RARITY_WEIGHTS.get(u['rarity'], 10) for u in pool]
        chosen = []
        for _ in range(min(count, len(pool))):
            total = sum(weights)
            r = random.uniform(0, total)
            cumulative = 0
            for i, w in enumerate(weights):
                cumulative += w
                if r <= cumulative:
                    chosen.append(pool[i])
                    pool.pop(i)
                    weights.pop(i)
                    break
        return chosen

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.choices)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.choices)
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self._select()
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                idx = event.key - pygame.K_1
                if idx < len(self.choices):
                    self.selected = idx
                    self._select()

    def _select(self):
        if self.choices:
            upgrade = self.choices[self.selected]
            upgrade['apply'](self.game.player)
            self.game.player.upgrades_taken.append(upgrade['name'])
            self.active = False

    def update(self, dt):
        self.anim_timer += dt
        for i in range(len(self.card_offsets)):
            target = 0
            self.card_offsets[i] += (target - self.card_offsets[i]) * 10 * dt

    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        title = self.font_huge.render('CHOOSE UPGRADE', True, (255, 220, 100))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        hint = self.font_small.render('A/D or 1/2/3 to select, E/Enter to confirm', True, (150, 150, 150))
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 40))

        card_w, card_h = 260, 320
        spacing = 40
        total_w = len(self.choices) * card_w + (len(self.choices) - 1) * spacing
        start_x = SCREEN_W // 2 - total_w // 2

        for i, upgrade in enumerate(self.choices):
            cx = start_x + i * (card_w + spacing)
            cy = SCREEN_H // 2 - card_h // 2 + int(self.card_offsets[i])
            selected = (i == self.selected)
            rcolor = RARITY_COLORS.get(upgrade['rarity'], (150, 150, 150))

            # Glow effect for selected
            if selected:
                glow = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
                t = math.sin(self.anim_timer * 4) * 0.5 + 0.5
                ga = int(80 + 60 * t)
                pygame.draw.rect(glow, (*rcolor, ga), (0, 0, card_w + 20, card_h + 20), border_radius=15)
                surface.blit(glow, (cx - 10, cy - 10))

            bg_color = (30, 30, 60) if selected else (20, 20, 40)
            pygame.draw.rect(surface, bg_color, (cx, cy, card_w, card_h), border_radius=10)
            border_w = 3 if selected else 2
            pygame.draw.rect(surface, rcolor, (cx, cy, card_w, card_h), border_w, border_radius=10)

            # Rarity label
            rar_txt = self.font_small.render(upgrade['rarity'].upper(), True, rcolor)
            surface.blit(rar_txt, (cx + card_w // 2 - rar_txt.get_width() // 2, cy + 15))

            # Icon placeholder (colored square)
            icon_rect = pygame.Rect(cx + card_w // 2 - 30, cy + 40, 60, 60)
            pygame.draw.rect(surface, rcolor, icon_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 0, 0, 0), icon_rect, 2, border_radius=8)
            num_txt = self.font_large.render(str(i + 1), True, (0, 0, 0))
            surface.blit(num_txt, (icon_rect.centerx - num_txt.get_width() // 2, icon_rect.centery - num_txt.get_height() // 2))

            # Name
            name_txt = self.font_large.render(upgrade['name'], True, (255, 255, 255) if selected else (200, 200, 200))
            if name_txt.get_width() > card_w - 20:
                name_txt = self.font_med.render(upgrade['name'], True, (255, 255, 255) if selected else (200, 200, 200))
            surface.blit(name_txt, (cx + card_w // 2 - name_txt.get_width() // 2, cy + 115))

            # Desc (word wrap)
            words = upgrade['desc'].split()
            lines = []
            cur = ''
            for word in words:
                test = (cur + ' ' + word).strip()
                if self.font_small.size(test)[0] <= card_w - 20:
                    cur = test
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
            for li, line in enumerate(lines):
                lt = self.font_small.render(line, True, (180, 180, 200))
                surface.blit(lt, (cx + card_w // 2 - lt.get_width() // 2, cy + 145 + li * 16))

        import math

class PowerUpSelection(UpgradeScreen):
    pass