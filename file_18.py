import pygame
import random
from settings import *

UPGRADE_POOL = [
    # (id, name, description, rarity, stat_changes)
    ('max_hp_up',     'Iron Heart',      '+30 Max HP',              'common',    {'max_hp': 30}),
    ('hp_regen',      'Regeneration',    '+1 HP/sec regen',         'uncommon',  {'hp_regen': 1}),
    ('move_speed',    'Swift Boots',     '+15% Move Speed',         'common',    {'speed_mult': 0.15}),
    ('dash_cd',       'Dash Mastery',    '-25% Dash Cooldown',      'uncommon',  {'dash_cd_mult': -0.25}),
    ('dash_charges',  'Double Dash',     '+1 Dash Charge',          'rare',      {'dash_charges': 1}),
    ('damage_up',     'Power Surge',     '+20% Damage',             'uncommon',  {'damage_mult': 0.20}),
    ('fire_rate',     'Rapid Fire',      '+20% Fire Rate',          'common',    {'fire_rate_mult': 0.20}),
    ('crit_chance',   'Eagle Eye',       '+15% Crit Chance',        'uncommon',  {'crit_chance': 0.15}),
    ('crit_damage',   'Executioner',     '+50% Crit Damage',        'rare',      {'crit_damage': 0.50}),
    ('pierce',        'Penetrator',      'Bullets pierce 1 extra',  'rare',      {'pierce': 1}),
    ('bounce',        'Ricochet',        'Bullets bounce once',     'rare',      {'bounce': 1}),
    ('lifesteal',     'Vampiric',        '5% Life Steal on hit',    'rare',      {'lifesteal': 0.05}),
    ('aoe_size',      'Blast Radius',    '+25% AoE Size',           'uncommon',  {'aoe_mult': 0.25}),
    ('shield',        'Force Field',     'Gain 50 Shield HP',       'uncommon',  {'shield': 50}),
    ('magnet',        'Magnetism',       '2x Coin/XP pickup range', 'common',    {'pickup_range': 2.0}),
    ('ammo_up',       'Extended Mag',    '+50% Max Ammo',           'common',    {'ammo_mult': 0.50}),
    ('reload_speed',  'Speed Loader',    '-30% Reload Time',        'common',    {'reload_mult': -0.30}),
    ('explosion_on_kill', 'Chain Reaction', 'Enemies explode on death', 'legendary', {'explosion_on_kill': True}),
    ('freeze_on_hit', 'Frost Touch',     '20% chance to slow enemy','uncommon',  {'freeze_on_hit': 0.20}),
    ('burn_on_hit',   'Pyromaniac',      '25% chance to ignite',    'uncommon',  {'burn_on_hit': 0.25}),
    ('coin_mult',     'Gold Rush',       '2x Coin Drops',           'uncommon',  {'coin_mult': 2.0}),
    ('score_mult',    'High Scorer',     '1.5x Score Multiplier',   'common',    {'score_mult': 1.5}),
    ('projectile_size','Big Shots',      '+50% Projectile Size',    'common',    {'proj_size': 0.50}),
    ('multishot',     'Twin Barrels',    'Fire 2 extra projectiles','legendary', {'multishot': 2}),
    ('ability_cd',    'Cooldown Reduction','-20% Ability Cooldown', 'uncommon',  {'ability_cd_mult': -0.20}),
]

RARITY_COLORS = {
    'common':    (180, 180, 180),
    'uncommon':  (80, 200, 80),
    'rare':      (80, 120, 255),
    'legendary': (255, 165, 0),
}

RARITY_WEIGHTS = {
    'common': 50,
    'uncommon': 30,
    'rare': 15,
    'legendary': 5,
}

class UpgradeCard:
    def __init__(self, data):
        self.id = data[0]
        self.name = data[1]
        self.description = data[2]
        self.rarity = data[3]
        self.stats = data[4]
        self.color = RARITY_COLORS[self.rarity]

class UpgradeScreen:
    def __init__(self, game):
        self.game = game
        self.cards = []
        self.selected = None
        self.hovered = None
        self.active = False
        self.font_big = pygame.font.SysFont('monospace', 24, bold=True)
        self.font_med = pygame.font.SysFont('monospace', 16)
        self.font_small = pygame.font.SysFont('monospace', 13)
        self.anim_t = 0
        self.card_rects = []

    def show(self, num_cards=3):
        self.cards = self._pick_cards(num_cards)
        self.selected = None
        self.hovered = None
        self.active = True
        self.anim_t = 0
        self.card_rects = []

    def _pick_cards(self, n):
        pool = list(UPGRADE_POOL)
        weights = [RARITY_WEIGHTS[d[3]] for d in pool]
        chosen = []
        seen_ids = set()
        attempts = 0
        while len(chosen) < n and attempts < 100:
            attempts += 1
            total = sum(weights)
            r = random.uniform(0, total)
            cum = 0
            for i, w in enumerate(weights):
                cum += w
                if r <= cum:
                    data = pool[i]
                    if data[0] not in seen_ids:
                        chosen.append(UpgradeCard(data))
                        seen_ids.add(data[0])
                    break
        return chosen

    def update(self, dt):
        if not self.active:
            return
        self.anim_t += dt
        mx, my = pygame.mouse.get_pos()
        self.hovered = None
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(mx, my):
                self.hovered = i

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered is not None:
                self.selected = self.hovered
                self._apply_upgrade(self.cards[self.selected])
                self.active = False
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.active = False
            return True
        return False

    def _apply_upgrade(self, card):
        p = self.game.player
        stats = card.stats
        
        if 'max_hp' in stats:
            p.max_hp += stats['max_hp']
            p.hp = min(p.hp + stats['max_hp'], p.max_hp)
        if 'hp_regen' in stats:
            p.hp_regen = getattr(p, 'hp_regen', 0) + stats['hp_regen']
        if 'speed_mult' in stats:
            p.speed_base *= (1 + stats['speed_mult'])
        if 'dash_cd_mult' in stats:
            p.dash_cooldown_max *= (1 + stats['dash_cd_mult'])
        if 'dash_charges' in stats:
            p.dash_charges_max = getattr(p, 'dash_charges_max', 1) + stats['dash_charges']
        if 'damage_mult' in stats:
            p.damage_mult = getattr(p, 'damage_mult', 1.0) * (1 + stats['damage_mult'])
        if 'fire_rate_mult' in stats:
            p.fire_rate_mult = getattr(p, 'fire_rate_mult', 1.0) * (1 + stats['fire_rate_mult'])
        if 'crit_chance' in stats:
            p.crit_chance = min(getattr(p, 'crit_chance', 0) + stats['crit_chance'], 0.95)
        if 'crit_damage' in stats:
            p.crit_damage = getattr(p, 'crit_damage', 1.5) + stats['crit_damage']
        if 'pierce' in stats:
            p.pierce = getattr(p, 'pierce', 0) + stats['pierce']
        if 'bounce' in stats:
            p.bounce = getattr(p, 'bounce', 0) + stats['bounce']
        if 'lifesteal' in stats:
            p.lifesteal = getattr(p, 'lifesteal', 0) + stats['lifesteal']
        if 'aoe_mult' in stats:
            p.aoe_mult = getattr(p, 'aoe_mult', 1.0) * (1 + stats['aoe_mult'])
        if 'shield' in stats:
            p.shield = getattr(p, 'shield', 0) + stats['shield']
            p.max_shield = getattr(p, 'max_shield', 0) + stats['shield']
        if 'pickup_range' in stats:
            p.pickup_range = getattr(p, 'pickup_range', 1.0) * stats['pickup_range']
        if 'ammo_mult' in stats:
            p.ammo_mult = getattr(p, 'ammo_mult', 1.0) * (1 + stats['ammo_mult'])
        if 'reload_mult' in stats:
            p.reload_mult = getattr(p, 'reload_mult', 1.0) * (1 + stats['reload_mult'])
        if 'explosion_on_kill' in stats:
            p.explosion_on_kill = True
        if 'freeze_on_hit' in stats:
            p.freeze_on_hit = getattr(p, 'freeze_on_hit', 0) + stats['freeze_on_hit']
        if 'burn_on_hit' in stats:
            p.burn_on_hit = getattr(p, 'burn_on_hit', 0) + stats['burn_on_hit']
        if 'coin_mult' in stats:
            p.coin_mult = getattr(p, 'coin_mult', 1.0) * stats['coin_mult']
        if 'score_mult' in stats:
            p.score_mult = getattr(p, 'score_mult', 1.0) * stats['score_mult']
        if 'proj_size' in stats:
            p.proj_size_mult = getattr(p, 'proj_size_mult', 1.0) * (1 + stats['proj_size'])
        if 'multishot' in stats:
            p.multishot = getattr(p, 'multishot', 0) + stats['multishot']
        if 'ability_cd_mult' in stats:
            p.ability_cd_mult = getattr(p, 'ability_cd_mult', 1.0) * (1 + stats['ability_cd_mult'])

        self.game.upgrades_taken.append(card.id)

    def draw(self, surface):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = self.font_big.render("CHOOSE AN UPGRADE", True, (255, 220, 50))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        card_w, card_h = 280, 200
        total_w = len(self.cards) * card_w + (len(self.cards) - 1) * 30
        start_x = SCREEN_W // 2 - total_w // 2
        start_y = SCREEN_H // 2 - card_h // 2

        self.card_rects = []
        for i, card in enumerate(self.cards):
            cx = start_x + i * (card_w + 30)
            cy = start_y
            offset_y = 0
            if self.hovered == i:
                import math
                offset_y = -10 + int(4 * math.sin(self.anim_t * 4))

            rect = pygame.Rect(cx, cy + offset_y, card_w, card_h)
            self.card_rects.append(rect)

            border_color = card.color if self.hovered == i else tuple(c // 2 for c in card.color)
            pygame.draw.rect(surface, (20, 20, 35), rect, border_radius=8)
            pygame.draw.rect(surface, border_color, rect, 3, border_radius=8)

            rarity_surf = self.font_small.render(card.rarity.upper(), True, card.color)
            surface.blit(rarity_surf, (cx + 10, cy + offset_y + 10))

            name_surf = self.font_med.render(card.name, True, (240, 240, 240))
            surface.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, cy + offset_y + 50))

            desc_surf = self.font_small.render(card.description, True, (180, 180, 180))
            surface.blit(desc_surf, (cx + card_w // 2 - desc_surf.get_width() // 2, cy + offset_y + 90))

            stat_y = cy + offset_y + 130
            for stat_k, stat_v in card.stats.items():
                if isinstance(stat_v, bool):
                    txt = f"  {stat_k}: ON"
                elif isinstance(stat_v, float):
                    txt = f"  {stat_k}: {stat_v:+.0%}" if abs(stat_v) <= 5 else f"  {stat_k}: x{stat_v:.1f}"
                else:
                    txt = f"  {stat_k}: {stat_v:+d}"
                s = self.font_small.render(txt, True, (120, 220, 120))
                surface.blit(s, (cx + 10, stat_y))
                stat_y += 16

        hint = self.font_small.render("Click a card to select", True, (120, 120, 120))
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 60))