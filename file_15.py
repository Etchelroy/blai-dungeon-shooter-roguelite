import pygame
import random
from settings import *

SHOP_ITEMS = [
    {'name': 'Speed Boost', 'desc': '+20% move speed', 'cost': 50, 'rarity': 'common', 'apply': lambda p: setattr(p, 'speed', p.speed * 1.2)},
    {'name': 'HP Up', 'desc': '+30 max HP, full heal', 'cost': 60, 'rarity': 'common', 'apply': lambda p: (setattr(p, 'max_hp', p.max_hp + 30), setattr(p, 'hp', p.max_hp))},
    {'name': 'Damage Up', 'desc': '+25% weapon damage', 'cost': 80, 'rarity': 'uncommon', 'apply': lambda p: setattr(p, 'damage_mult', getattr(p, 'damage_mult', 1.0) * 1.25)},
    {'name': 'Fire Rate Up', 'desc': '+20% fire rate', 'cost': 70, 'rarity': 'uncommon', 'apply': lambda p: _boost_firerate(p)},
    {'name': 'Extra Dash', 'desc': '-30% dash cooldown', 'cost': 90, 'rarity': 'uncommon', 'apply': lambda p: setattr(p, 'dash_cooldown', p.dash_cooldown * 0.7)},
    {'name': 'Shield', 'desc': '+50 armor', 'cost': 100, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'armor', getattr(p, 'armor', 0) + 50)},
    {'name': 'Vampiric', 'desc': 'Lifesteal 5% damage dealt', 'cost': 120, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'lifesteal', getattr(p, 'lifesteal', 0) + 0.05)},
    {'name': 'Explosive Rounds', 'desc': 'Bullets explode on hit', 'cost': 150, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'explosive_rounds', True)},
    {'name': 'Ammo Up', 'desc': '+50% ammo capacity', 'cost': 60, 'rarity': 'common', 'apply': lambda p: _boost_ammo(p)},
    {'name': 'Full Heal', 'desc': 'Restore all HP', 'cost': 40, 'rarity': 'common', 'apply': lambda p: setattr(p, 'hp', p.max_hp)},
    {'name': 'Crit Chance', 'desc': '+15% crit chance', 'cost': 100, 'rarity': 'uncommon', 'apply': lambda p: setattr(p, 'crit_chance', getattr(p, 'crit_chance', 0.05) + 0.15)},
    {'name': 'Piercing', 'desc': 'Bullets pierce 1 extra enemy', 'cost': 130, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'pierce_count', getattr(p, 'pierce_count', 0) + 1)},
    {'name': 'Lucky Coin', 'desc': '+20% coin drops', 'cost': 30, 'rarity': 'common', 'apply': lambda p: setattr(p, 'coin_mult', getattr(p, 'coin_mult', 1.0) * 1.2)},
    {'name': 'Berserker', 'desc': '+40% dmg below 30% HP', 'cost': 110, 'rarity': 'uncommon', 'apply': lambda p: setattr(p, 'berserker', True)},
    {'name': 'Ice Ammo', 'desc': 'Bullets slow enemies', 'cost': 120, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'ice_ammo', True)},
    {'name': 'Bouncy Bullets', 'desc': 'Bullets bounce once', 'cost': 140, 'rarity': 'rare', 'apply': lambda p: setattr(p, 'bounce_count', getattr(p, 'bounce_count', 0) + 1)},
    {'name': 'Turbo Reload', 'desc': '-40% reload time', 'cost': 80, 'rarity': 'uncommon', 'apply': lambda p: _boost_reload(p)},
    {'name': 'Mega Dash', 'desc': 'Dash damages enemies', 'cost': 160, 'rarity': 'epic', 'apply': lambda p: setattr(p, 'dash_damage', True)},
    {'name': 'Double Trouble', 'desc': 'Fire 2 projectiles', 'cost': 200, 'rarity': 'epic', 'apply': lambda p: setattr(p, 'double_shot', getattr(p, 'double_shot', False) or True)},
    {'name': 'Time Warp', 'desc': 'Kill streaks slow time', 'cost': 180, 'rarity': 'epic', 'apply': lambda p: setattr(p, 'time_warp', True)},
]

def _boost_firerate(p):
    for w in p.weapons:
        if hasattr(w, 'fire_rate'):
            w.fire_rate = max(0.05, w.fire_rate * 0.8)

def _boost_ammo(p):
    for w in p.weapons:
        if hasattr(w, 'max_ammo'):
            w.max_ammo = int(w.max_ammo * 1.5)
            w.current_ammo = w.max_ammo

def _boost_reload(p):
    for w in p.weapons:
        if hasattr(w, 'reload_time'):
            w.reload_time = max(0.3, w.reload_time * 0.6)

RARITY_COLORS = {
    'common': (180, 180, 180),
    'uncommon': (100, 200, 100),
    'rare': (80, 120, 255),
    'epic': (200, 50, 255),
}

class Shop:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.items = []
        self.selected = 0
        self.font_large = pygame.font.SysFont('monospace', 24, bold=True)
        self.font_med = pygame.font.SysFont('monospace', 16, bold=True)
        self.font_small = pygame.font.SysFont('monospace', 12, bold=True)
        self.scroll_offset = 0
        self.message = ''
        self.message_timer = 0

    def open(self):
        self.active = True
        self.items = random.sample(SHOP_ITEMS, min(6, len(SHOP_ITEMS)))
        self.selected = 0
        self.scroll_offset = 0
        self.message = ''

    def close(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                self._buy_selected()
            elif event.key == pygame.K_ESCAPE:
                self.close()

    def _buy_selected(self):
        item = self.items[self.selected]
        player = self.game.player
        coins = getattr(player, 'coins', 0)
        if coins >= item['cost']:
            player.coins = coins - item['cost']
            item['apply'](player)
            self.message = f"Bought: {item['name']}!"
            self.message_timer = 2.0
            self.items.pop(self.selected)
            self.selected = min(self.selected, max(0, len(self.items) - 1))
        else:
            self.message = "Not enough coins!"
            self.message_timer = 1.5

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        panel_w, panel_h = 600, 500
        panel_x = SCREEN_W // 2 - panel_w // 2
        panel_y = SCREEN_H // 2 - panel_h // 2

        pygame.draw.rect(surface, (20, 20, 40), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, (100, 80, 200), (panel_x, panel_y, panel_w, panel_h), 3)

        title = self.font_large.render('=== SHOP ===', True, (255, 220, 100))
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, panel_y + 15))

        coins_txt = self.font_med.render(f'Coins: ${getattr(self.game.player, "coins", 0)}', True, (255, 220, 50))
        surface.blit(coins_txt, (panel_x + 20, panel_y + 50))

        esc_txt = self.font_small.render('ESC=Close  E/Enter=Buy  W/S=Navigate', True, (150, 150, 150))
        surface.blit(esc_txt, (panel_x + 20, panel_y + panel_h - 30))

        item_y = panel_y + 80
        for i, item in enumerate(self.items):
            selected = (i == self.selected)
            row_color = (40, 40, 80) if selected else (25, 25, 50)
            border_color = RARITY_COLORS.get(item['rarity'], (150, 150, 150))
            if selected:
                border_color = (255, 255, 100)

            pygame.draw.rect(surface, row_color, (panel_x + 10, item_y, panel_w - 20, 60))
            pygame.draw.rect(surface, border_color, (panel_x + 10, item_y, panel_w - 20, 60), 2)

            name_txt = self.font_med.render(item['name'], True, border_color)
            surface.blit(name_txt, (panel_x + 20, item_y + 8))

            desc_txt = self.font_small.render(item['desc'], True, (200, 200, 200))
            surface.blit(desc_txt, (panel_x + 20, item_y + 28))

            rarity_txt = self.font_small.render(item['rarity'].upper(), True, RARITY_COLORS.get(item['rarity'], (150, 150, 150)))
            surface.blit(rarity_txt, (panel_x + 380, item_y + 8))

            cost_color = (100, 255, 100) if getattr(self.game.player, 'coins', 0) >= item['cost'] else (255, 80, 80)
            cost_txt = self.font_med.render(f'${item["cost"]}', True, cost_color)
            surface.blit(cost_txt, (panel_x + panel_w - 80, item_y + 18))

            item_y += 68

        if self.message and self.message_timer > 0:
            msg_txt = self.font_med.render(self.message, True, (255, 220, 100))
            surface.blit(msg_txt, (SCREEN_W // 2 - msg_txt.get_width() // 2, panel_y + panel_h - 55))