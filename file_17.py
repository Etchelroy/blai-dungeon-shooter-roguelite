import pygame
import random
from settings import *

UPGRADE_POOL = [
    {'name': 'Max HP Up', 'desc': '+25 Max HP, heal 15', 'rarity': 'common', 'cost': 30,
     'apply': lambda p: (setattr(p, 'max_hp', p.max_hp+25), setattr(p, 'hp', min(p.max_hp, p.hp+15)))},
    {'name': 'Speed Boost', 'desc': '+15% move speed', 'rarity': 'common', 'cost': 25,
     'apply': lambda p: setattr(p, 'speed', p.speed * 1.15)},
    {'name': 'Damage Up', 'desc': '+20% weapon damage', 'rarity': 'uncommon', 'cost': 40,
     'apply': lambda p: setattr(p, 'damage_mult', getattr(p,'damage_mult',1.0)*1.2)},
    {'name': 'Fire Rate', 'desc': '+20% fire rate', 'rarity': 'uncommon', 'cost': 40,
     'apply': lambda p: setattr(p, 'fire_rate_mult', getattr(p,'fire_rate_mult',1.0)*1.2)},
    {'name': 'Dash Recharge', 'desc': '-0.3s dash cooldown', 'rarity': 'uncommon', 'cost': 35,
     'apply': lambda p: setattr(p, 'dash_cooldown_max', max(0.3, p.dash_cooldown_max-0.3))},
    {'name': 'Coin Magnet', 'desc': 'Coins auto-collect nearby', 'rarity': 'common', 'cost': 20,
     'apply': lambda p: setattr(p, 'coin_magnet', True)},
    {'name': 'Armor', 'desc': '-15% damage taken', 'rarity': 'uncommon', 'cost': 45,
     'apply': lambda p: setattr(p, 'armor', getattr(p,'armor',1.0)*0.85)},
    {'name': 'Vampiric', 'desc': '+3 HP per kill', 'rarity': 'rare', 'cost': 60,
     'apply': lambda p: setattr(p, 'lifesteal_per_kill', getattr(p,'lifesteal_per_kill',0)+3)},
    {'name': 'Explosive Rounds', 'desc': 'Bullets explode on hit', 'rarity': 'rare', 'cost': 70,
     'apply': lambda p: setattr(p, 'explosive_rounds', True)},
    {'name': 'Chain Lightning', 'desc': 'Hits chain to nearby enemies', 'rarity': 'rare', 'cost': 65,
     'apply': lambda p: setattr(p, 'chain_hits', getattr(p,'chain_hits',0)+1)},
    {'name': 'Ammo Pack', 'desc': 'Refill all weapon ammo', 'rarity': 'common', 'cost': 15,
     'apply': lambda p: _refill_ammo(p)},
    {'name': 'Double Dash', 'desc': '+1 dash charge', 'rarity': 'uncommon', 'cost': 50,
     'apply': lambda p: setattr(p, 'dash_charges', getattr(p,'dash_charges',1)+1)},
    {'name': 'Critical Hit', 'desc': '+15% crit chance', 'rarity': 'uncommon', 'cost': 45,
     'apply': lambda p: setattr(p, 'crit_chance', getattr(p,'crit_chance',0.05)+0.15)},
    {'name': 'Adrenaline', 'desc': '+10% speed when low HP', 'rarity': 'rare', 'cost': 55,
     'apply': lambda p: setattr(p, 'adrenaline', True)},
    {'name': 'Shield Bubble', 'desc': 'Absorbs 1 hit every 10s', 'rarity': 'rare', 'cost': 75,
     'apply': lambda p: setattr(p, 'shield_cooldown', 10.0)},
    {'name': 'Rapid Reload', 'desc': '-30% reload time', 'rarity': 'uncommon', 'cost': 40,
     'apply': lambda p: setattr(p, 'reload_mult', getattr(p,'reload_mult',1.0)*0.7)},
    {'name': 'Ricochet', 'desc': 'Bullets bounce once', 'rarity': 'rare', 'cost': 60,
     'apply': lambda p: setattr(p, 'ricochet', True)},
    {'name': 'Overclock', 'desc': 'Ability cooldown -25%', 'rarity': 'rare', 'cost': 65,
     'apply': lambda p: setattr(p, 'ability_cd_mult', getattr(p,'ability_cd_mult',1.0)*0.75)},
    {'name': 'Healing Aura', 'desc': '+1 HP/sec regen', 'rarity': 'uncommon', 'cost': 50,
     'apply': lambda p: setattr(p, 'hp_regen', getattr(p,'hp_regen',0)+1)},
    {'name': 'Berserker', 'desc': '+5% dmg per combo hit', 'rarity': 'rare', 'cost': 70,
     'apply': lambda p: setattr(p, 'berserker', True)},
]

RARITY_COLORS = {
    'common': (180,180,180),
    'uncommon': (80,220,80),
    'rare': (100,100,255),
    'legendary': (255,180,0),
}

def _refill_ammo(player):
    if hasattr(player, 'weapons'):
        for w in player.weapons:
            if hasattr(w, 'ammo') and hasattr(w, 'max_ammo'):
                w.ammo = w.max_ammo


class ShopItem:
    def __init__(self, data):
        self.data = data
        self.name = data['name']
        self.desc = data['desc']
        self.rarity = data['rarity']
        self.cost = data['cost']
        self.rect = pygame.Rect(0,0,0,0)
        self.hover = False

    def apply(self, player):
        try:
            self.data['apply'](player)
        except Exception as e:
            print(f"[Shop] Error applying {self.name}: {e}")


class Shop:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.active = False
        self.items = []
        self.font_lg = pygame.font.SysFont('monospace', 36, bold=True)
        self.font_md = pygame.font.SysFont('monospace', 22, bold=True)
        self.font_sm = pygame.font.SysFont('monospace', 16)
        self.reroll_cost = 10
        self.reroll_rect = pygame.Rect(0,0,0,0)
        self.close_rect = pygame.Rect(0,0,0,0)

    def open(self):
        self.active = True
        self._generate_items()

    def close(self):
        self.active = False

    def _generate_items(self):
        weights = {'common': 50, 'uncommon': 30, 'rare': 18, 'legendary': 2}
        pool = UPGRADE_POOL[:]
        random.shuffle(pool)
        chosen = random.sample(pool, min(4, len(pool)))
        self.items = [ShopItem(d) for d in chosen]
        card_w = 260
        card_h = 160
        gap = 20
        total_w = len(self.items) * card_w + (len(self.items)-1)*gap
        start_x = self.screen_w//2 - total_w//2
        start_y = self.screen_h//2 - card_h//2
        for i, item in enumerate(self.items):
            item.rect = pygame.Rect(start_x + i*(card_w+gap), start_y, card_w, card_h)

    def handle_event(self, event, player):
        if not self.active:
            return False
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for item in self.items:
                item.hover = item.rect.collidepoint(mx, my)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for item in self.items:
                if item.rect.collidepoint(mx, my):
                    if player.coins >= item.cost:
                        player.coins -= item.cost
                        item.apply(player)
                        self.items.remove(item)
                        return True
            if self.reroll_rect.collidepoint(mx, my):
                if player.coins >= self.reroll_cost:
                    player.coins -= self.reroll_cost
                    self._generate_items()
                    return True
            if self.close_rect.collidepoint(mx, my):
                self.close()
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        return False

    def draw(self, surf, player):
        if not self.active:
            return
        # dim background
        dim = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        dim.fill((0,0,0,180))
        surf.blit(dim, (0,0))
        # title
        title = self.font_lg.render("[ SHOP ]", True, (255,220,80))
        surf.blit(title, (self.screen_w//2 - title.get_width()//2, 80))
        coins_txt = self.font_md.render(f"Coins: {player.coins}", True, (255,220,60))
        surf.blit(coins_txt, (self.screen_w//2 - coins_txt.get_width()//2, 130))
        # items
        for item in self.items:
            rc = RARITY_COLORS.get(item.rarity, (200,200,200))
            bg = (30,30,50) if not item.hover else (50,50,80)
            pygame.draw.rect(surf, bg, item.rect, border_radius=8)
            pygame.draw.rect(surf, rc, item.rect, 3, border_radius=8)
            name_txt = self.font_md.render(item.name, True, rc)
            surf.blit(name_txt, (item.rect.x+10, item.rect.y+10))
            rarity_txt = self.font_sm.render(item.rarity.upper
# filename: src/wave_manager.py
```python
import pygame
import random
from settings import *

class WaveManager:
    def __init__(self, game):
        self.game = game
        self.wave = 0
        self.enemies_remaining = 0
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        self.wave_active = False
        self.between_waves = False
        self.between_timer = 0
        self.between_duration = 3.0
        self.boss_wave = False
        self.wave_complete_callbacks = []
        self.total_killed = 0

    def start_next_wave(self):
        self.wave += 1
        self.between_waves = False
        self.wave_active = True
        self.boss_wave = (self.wave % 5 == 0)
        self.enemies_to_spawn = self._generate_spawn_list()
        self.enemies_remaining = len(self.enemies_to_spawn)
        self.spawn_timer = 0
        if hasattr(self.game, 'hud'):
            self.game.hud.show_wave_banner(self.wave)

    def _generate_spawn_list(self):
        spawns = []
        if self.boss_wave:
            boss_idx = min((self.wave // 5) - 1, 2)
            spawns.append(('boss', boss_idx))
            return spawns
        
        wave = self.wave
        count = 5 + wave * 2
        count = min(count, 30)
        
        tier1 = ['grunt', 'shooter', 'rusher']
        tier2 = ['shielder', 'bomber', 'summoner']
        tier3 = ['phantom', 'titan', 'sniper', 'leech']
        
        for _ in range(count):
            roll = random.random()
            if wave <= 3:
                spawns.append(('enemy', random.choice(tier1)))
            elif wave <= 6:
                if roll < 0.6:
                    spawns.append(('enemy', random.choice(tier1)))
                else:
                    spawns.append(('enemy', random.choice(tier2)))
            else:
                if roll < 0.3:
                    spawns.append(('enemy', random.choice(tier1)))
                elif roll < 0.7:
                    spawns.append(('enemy', random.choice(tier2)))
                else:
                    spawns.append(('enemy', random.choice(tier3)))
        
        random.shuffle(spawns)
        return spawns

    def update(self, dt):
        if self.between_waves:
            self.between_timer += dt
            if self.between_timer >= self.between_duration:
                self.start_next_wave()
            return

        if not self.wave_active:
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.enemies_to_spawn:
            self.spawn_timer = 0
            entry = self.enemies_to_spawn.pop(0)
            self._do_spawn(entry)

        alive = len([e for e in self.game.enemies if e.alive])
        if not self.enemies_to_spawn and alive == 0 and self.wave_active:
            self._complete_wave()

    def _do_spawn(self, entry):
        kind = entry[0]
        pos = self._get_spawn_pos()
        
        if kind == 'boss':
            boss_idx = entry[1]
            self.game.spawn_boss(boss_idx, pos)
        else:
            etype = entry[1]
            self.game.spawn_enemy(etype, pos)

    def _get_spawn_pos(self):
        arena = self.game.arena
        player = self.game.player
        px, py = player.x, player.y
        
        for _ in range(20):
            x = random.randint(2, arena.width - 3) * TILE_SIZE * SCALE
            y = random.randint(2, arena.height - 3) * TILE_SIZE * SCALE
            dist = ((x - px)**2 + (y - py)**2)**0.5
            if dist > 300:
                tx = int(x / (TILE_SIZE * SCALE))
                ty = int(y / (TILE_SIZE * SCALE))
                if arena.is_walkable(tx, ty):
                    return (x, y)
        
        return (px + 400, py + 400)

    def _complete_wave(self):
        self.wave_active = False
        self.between_waves = True
        self.between_timer = 0
        self.game.on_wave_complete(self.wave)

    def should_show_shop(self):
        return self.wave > 0 and self.wave % 3 == 0

    def get_between_progress(self):
        return self.between_timer / self.between_duration

    def force_start(self):
        self.between_waves = False
        self.between_timer = self.between_duration
        self.start_next_wave()