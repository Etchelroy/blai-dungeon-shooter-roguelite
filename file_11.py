import math, random, pygame
from src.utils import vec2_norm, angle_to
from settings import TILE_SIZE

class Bullet:
    def __init__(self, x, y, vx, vy, dmg, owner='player', color=(255,220,50),
                 size=4, life=2.0, pierce=0, aoe=0):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.dmg=dmg; self.owner=owner; self.color=color
        self.size=size; self.life=life; self.pierce=pierce
        self.aoe=aoe; self.alive=True
        self.hit_set=set(); self.trail=[]
        self.returning=False; self.return_target=None
        self.dot=0; self.dot_dur=0
        self.chain=0; self.chain_targets=[]

    def update(self, dt, tilemap):
        if not self.alive: return
        self.life -= dt
        if self.life <= 0:
            if self.aoe > 0:
                self._explode_pending = True
            self.alive = False
            return
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        if tilemap.is_solid_world(self.x, self.y):
            if self.aoe > 0:
                self._explode_pending = True
            self.alive = False

    def draw(self, surf, cx, cy):
        sx = int(self.x - cx); sy = int(self.y - cy)
        for i,(tx,ty) in enumerate(self.trail):
            t = (i+1)/max(len(self.trail),1)
            c = tuple(int(v*t) for v in self.color)
            pygame.draw.circle(surf, c, (int(tx-cx),int(ty-cy)), max(1,int(self.size*t*0.7)))
        pygame.draw.circle(surf, self.color, (sx,sy), self.size)
        # glow
        glow = pygame.Surface((self.size*4,self.size*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color,60), (self.size*2,self.size*2), self.size*2)
        surf.blit(glow, (sx-self.size*2, sy-self.size*2), special_flags=pygame.BLEND_RGBA_ADD)

WEAPON_DEFS = {
    'pistol':    {'name':'Pistol',    'ammo':-1, 'fire_rate':0.25, 'dmg':18, 'speed':600, 'color':(255,220,50),  'size':3, 'spread':0.05},
    'shotgun':   {'name':'Shotgun',   'ammo':40, 'fire_rate':0.7,  'dmg':12, 'speed':500, 'color':(255,160,50),  'size':3, 'pellets':6, 'spread':0.35},
    'rifle':     {'name':'Rifle',     'ammo':90, 'fire_rate':0.12, 'dmg':22, 'speed':900, 'color':(100,255,100), 'size':3, 'spread':0.02, 'pierce':2},
    'rocket':    {'name':'Rocket',    'ammo':20, 'fire_rate':1.0,  'dmg':60, 'speed':400, 'color':(255,80,20),   'size':5, 'spread':0.0,  'aoe':80},
    'chaingun':  {'name':'Chaingun',  'ammo':200,'fire_rate':0.07, 'dmg':8,  'speed':700, 'color':(200,200,50),  'size':2, 'spread':0.12},
    'sniper':    {'name':'Sniper',    'ammo':15, 'fire_rate':1.5,  'dmg':100,'speed':1200,'color':(50,200,255),  'size':3, 'spread':0.0, 'pierce':10},
    'flamethrower':{'name':'Flame',  'ammo':100,'fire_rate':0.05, 'dmg':5,  'speed':250, 'color':(255,100,20),  'size':5, 'spread':0.4, 'dot':3,'dot_dur':2.0,'life':0.4},
    'plasma':    {'name':'Plasma',   'ammo':50, 'fire_rate':0.3,  'dmg':35, 'speed':550, 'color':(180,80,255),  'size':5, 'spread':0.08,'chain':3},
}

class WeaponSystem:
    def __init__(self):
        self.weapons = list(WEAPON_DEFS.keys())
        self.current = 0
        self.cooldowns = {k:0.0 for k in self.weapons}
        self.ammo = {k: WEAPON_DEFS[k]['ammo'] for k in self.weapons}

    def current_weapon(self):
        return self.weapons[self.current]

    def current_def(self):
        return WEAPON_DEFS[self.current_weapon()]

    def next_weapon(self):
        self.current = (self.current + 1) % len(self.weapons)

    def prev_weapon(self):
        self.current = (self.current - 1) % len(self.weapons)

    def switch_to(self, idx):
        self.current = idx % len(self.weapons)

    def update(self, dt):
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= dt

    def can_fire(self):
        wn = self.current_weapon()
        d = self.current_def()
        if self.cooldowns[wn] > 0: return False
        if d['ammo'] != -1 and self.ammo[wn] <= 0: return False
        return True

    def fire(self, x, y, angle, owner='player'):
        wn = self.current_weapon()
        d = self.current_def()
        if not self.can_fire(): return []
        self.cooldowns[wn] = d['fire_rate']
        if d['ammo'] != -1:
            self.ammo[wn] -= 1
        bullets = []
        pellets = d.get('pellets', 1)
        for _ in range(pellets):
            a = angle + random.uniform(-d['spread'], d['spread'])
            spd = d['speed'] * random.uniform(0.95,1.05)
            b = Bullet(x,y, math.cos(a)*spd, math.sin(a)*spd,
                       d['dmg'], owner, d['color'], d.get('size',3),
                       d.get('life',2.0), d.get('pierce',0), d.get('aoe',0))
            b.dot = d.get('dot',0); b.dot_dur=d.get('dot_dur',0)
            b.chain = d.get('chain',0)
            bullets.append(b)
        return bullets