import pygame
import math
import random
from settings import TILE_SIZE, TILE_SCALE, TILE_PX

_cache = {}

def get_font(size):
    key = ('font', size)
    if key not in _cache:
        try:
            _cache[key] = pygame.font.SysFont('monospace', size, bold=True)
        except:
            _cache[key] = pygame.font.Font(None, size)
    return _cache[key]

def _make_surface(w, h, alpha=True):
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((w, h), flags)

def draw_pixel_rect(surf, color, x, y, w, h):
    pygame.draw.rect(surf, color, (x, y, w, h))

# --- Tile sprites ---
def make_floor_tile(variant=0):
    key = ('floor', variant)
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    colors = [(60,55,50),(65,60,55),(55,52,48)]
    base = colors[variant % len(colors)]
    s.fill(base)
    rng = random.Random(variant * 137)
    for _ in range(18):
        x = rng.randint(0, TILE_PX-2)
        y = rng.randint(0, TILE_PX-2)
        c = tuple(max(0,min(255,base[i]+rng.randint(-10,10))) for i in range(3))
        pygame.draw.rect(s, c, (x,y,2,2))
    _cache[key] = s
    return s

def make_wall_tile(variant=0):
    key = ('wall', variant)
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    colors = [(90,80,70),(80,75,65),(100,85,75)]
    base = colors[variant % len(colors)]
    s.fill(base)
    # brick pattern
    rng = random.Random(variant * 311)
    brick_h = TILE_PX // 3
    for row in range(3):
        offset = (row % 2) * (TILE_PX // 4)
        y = row * brick_h
        pygame.draw.line(s, (base[0]-20, base[1]-20, base[2]-20), (0,y), (TILE_PX,y), 2)
        for col in range(3):
            x = (col * TILE_PX // 2 + offset) % TILE_PX
            pygame.draw.line(s, (base[0]-15, base[1]-15, base[2]-15), (x,y), (x,y+brick_h), 1)
    _cache[key] = s
    return s

def make_lava_tile(t=0.0):
    s = _make_surface(TILE_PX, TILE_PX)
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            v = (math.sin(x*0.3+t*2)+math.sin(y*0.25-t*1.5)+2)/4
            r = int(180 + v*75)
            g = int(v*80)
            b = 0
            s.set_at((x,y),(clamp(r,0,255),clamp(g,0,255),b))
    return s

def clamp(v,lo,hi): return max(lo,min(hi,v))

def make_ice_tile():
    key = 'ice'
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    s.fill((160,210,240))
    rng = random.Random(42)
    for _ in range(8):
        x,y = rng.randint(0,TILE_PX-1), rng.randint(0,TILE_PX-1)
        pygame.draw.line(s,(200,230,255),(x,y),(x+rng.randint(-8,8),y+rng.randint(-8,8)),1)
    _cache[key] = s
    return s

def make_spike_tile():
    key = 'spike'
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    s.fill((55,55,60))
    pts_list = []
    for i in range(4):
        bx = i*(TILE_PX//4)
        pts = [(bx+TILE_PX//8, TILE_PX-4),(bx+TILE_PX//4, 6),(bx+TILE_PX//4+TILE_PX//8, TILE_PX-4)]
        pts_list.append(pts)
    for pts in pts_list:
        pygame.draw.polygon(s,(160,160,170),pts)
    _cache[key] = s
    return s

def make_poison_tile():
    key = 'poison'
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    s.fill((40,80,40))
    rng = random.Random(99)
    for _ in range(12):
        x,y = rng.randint(2,TILE_PX-3),rng.randint(2,TILE_PX-3)
        pygame.draw.circle(s,(60,160,60),(x,y),rng.randint(2,5))
    _cache[key] = s
    return s

# --- Entity sprites ---
def make_player_sprite(direction=0, frame=0):
    key = ('player', direction, frame)
    if key in _cache: return _cache[key]
    s = _make_surface(36, 36)
    # body
    pygame.draw.ellipse(s, (80,120,200), (6,10,24,20))
    # head
    pygame.draw.circle(s, (220,180,140), (18,10), 9)
    # eyes
    ex = 18 + int(math.cos(direction)*4)
    ey = 10 + int(math.sin(direction)*4)
    pygame.draw.circle(s,(20,20,20),(ex,ey),2)
    # gun indicator
    gx = 18 + int(math.cos(direction)*12)
    gy = 10 + int(math.sin(direction)*12)
    pygame.draw.line(s,(200,200,200),(18,10),(gx,gy),3)
    _cache[key] = s
    return s

def make_enemy_sprite(etype, frame=0, color=None):
    key = ('enemy', etype, frame)
    if key in _cache: return _cache[key]
    s = _make_surface(32, 32)
    colors = {
        0:(220,80,80), 1:(80,220,80), 2:(80,80,220),
        3:(220,220,80), 4:(220,80,220), 5:(80,220,220),
        6:(220,140,80), 7:(140,80,220), 8:(80,140,220), 9:(220,80,140)
    }
    c = color or colors.get(etype % 10, (200,200,200))
    if etype == 0:  # grunt - circle
        pygame.draw.circle(s,c,(16,16),13)
        pygame.draw.circle(s,(255,255,255),(20,12),3)
    elif etype == 1:  # runner - triangle
        pygame.draw.polygon(s,c,[(16,2),(30,30),(2,30)])
        pygame.draw.circle(s,(255,255,255),(16,14),3)
    elif etype == 2:  # tank - square
        pygame.draw.rect(s,c,(2,2,28,28))
        pygame.draw.rect(s,(255,255,255),(10,6,12,8))
    elif etype == 3:  # shooter - diamond
        pygame.draw.polygon(s,c,[(16,2),(30,16),(16,30),(2,16)])
        pygame.draw.circle(s,(255,255,255),(16,16),4)
    elif etype == 4:  # bomber - star
        for i in range(8):
            a = i * math.pi / 4
            x = 16 + int(math.cos(a)*13)
            y = 16 + int(math.sin(a)*13)
            pygame.draw.line(s,c,(16,16),(x,y),3)
        pygame.draw.circle(s,c,(16,16),7)
    elif etype == 5:  # speeder
        pygame.draw.ellipse(s,c,(2,8,28,16))
        pygame.draw.circle(s,(255,255,255),(20,16),3)
    elif etype == 6:  # shield
        pygame.draw.circle(s,c,(16,16),13)
        pygame.draw.arc(s,(180,220,255),(4,4,24,24),0,math.pi,4)
    elif etype == 7:  # sniper
        pygame.draw.rect(s,c,(6,8,20,16))
        pygame.draw.line(s,(200,200,200),(16,8),(28,2),2)
    elif etype == 8:  # swarm - small
        pygame.draw.circle(s,c,(16,16),8)
        for i in range(6):
            a = i*math.pi/3
            pygame.draw.circle(s,c,(16+int(math.cos(a)*10),16+int(math.sin(a)*10)),4)
    elif etype == 9:  # elite
        pygame.draw.polygon(s,c,[(16,2),(30,12),(25,28),(7,28),(2,12)])
        pygame.draw.circle(s,(255,255,200),(16,16),5)
    _cache[key] = s
    return s

def make_boss_sprite(btype, phase=0, frame=0):
    key = ('boss', btype, phase, frame)
    if key in _cache: return _cache[key]
    s = _make_surface(80, 80)
    phase_colors = [(220,60,60),(220,140,60),(220,60,220)]
    c = phase_colors[phase % 3]
    if btype == 0:  # Golem
        pygame.draw.rect(s,c,(10,15,60,55))
        pygame.draw.rect(s,(min(c[0]+40,255),min(c[1]+40,255),min(c[2]+40,255)),(20,5,40,25))
        pygame.draw.rect(s,(40,40,40),(25,12,12,10))
        pygame.draw.rect(s,(40,40,40),(45,12,12,10))
        if phase >= 1:
            pygame.draw.line(s,(255,100,100),(10,15),(70,70),3)
    elif btype == 1:  # Hydra
        pygame.draw.circle(s,c,(40,45),28)
        for i in range(3+phase):
            a = i*(2*math.pi/(3+phase)) - math.pi/2
            hx = 40+int(math.cos(a)*20)
            hy = 45+int(math.sin(a)*20)
            pygame.draw.circle(s,c,(hx,hy),10)
            pygame.draw.circle(s,(255,200,0),(hx,hy),3)
    elif btype == 2:  # Phantom
        pts = [(40,2),(75,20),(65,58),(15,58),(5,20)]
        pygame.draw.polygon(s,c,pts)
        pygame.draw.polygon(s,(255,255,255),pts,2)
        pygame.draw.circle(s,(200,220,255),(40,35),10)
        for i in range(phase+1):
            a = i*(2*math.pi/(phase+1))
            ox = int(math.cos(a)*15)
            oy = int(math.sin(a)*15)
            pygame.draw.circle(s,(255,220,100),(40+ox,35+oy),4)
    _cache[key] = s
    return s

def make_bullet_sprite(wtype):
    key = ('bullet', wtype)
    if key in _cache: return _cache[key]
    s = _make_surface(12, 6)
    colors = [(255,255,100),(255,140,50),(100,200,255),(255,80,80),(100,255,220),(255,120,0),(200,200,200),(0,200,255)]
    c = colors[wtype % len(colors)]
    pygame.draw.ellipse(s,c,(0,0,12,6))
    _cache[key] = s
    return s

def make_crate_sprite(hp_frac=1.0):
    key = ('crate', int(hp_frac*4))
    if key in _cache: return _cache[key]
    s = _make_surface(TILE_PX, TILE_PX)
    c = (160,110,60)
    if hp_frac < 0.5: c = (140,90,50)
    if hp_frac < 0.25: c = (120,70,40)
    pygame.draw.rect(s,c,(2,2,TILE_PX-4,TILE_PX-4))
    pygame.draw.rect(s,(100,70,30),(2,2,TILE_PX-4,TILE_PX-4),2)
    pygame.draw.line(s,(100,70,30),(2,2),(TILE_PX-4,TILE_PX-4),2)
    pygame.draw.line(s,(100,70,30),(TILE_PX-4,2),(2,TILE_PX-4),2)
    _cache[key] = s
    return s

def make_coin_sprite():
    key = 'coin'
    if key in _cache: return _cache[key]
    s = _make_surface(16,16)
    pygame.draw.circle(s,(255,215,0),(8,8),7)
    pygame.draw.circle(s,(200,170,0),(8,8),7,2)
    pygame.draw.circle(s,(255,240,100),(6,6),3)
    _cache[key] = s
    return s

def make_shield_sprite(radius):
    s = _make_surface(radius*2, radius*2)
    pygame.draw.circle(s,(100,180,255,80),(radius,radius),radius)
    pygame.draw.circle(s,(150,210,255,180),(radius,radius),radius,3)
    return s

def make_turret_sprite():
    key = 'turret'
    if key in _cache: return _cache[key]
    s = _make_surface(28,28)
    pygame.draw.circle(s,(100,100,120),(14,14),12)
    pygame.draw.rect(s,(150,150,180),(12,2,4,12))
    _cache[key] = s
    return s

def preload_all():
    for v in range(3):
        make_floor_tile(v)
        make_wall_tile(v)
    make_ice_tile()
    make_spike_tile()
    make_poison_tile()
    make_crate_sprite(1.0)
    make_coin_sprite()
    for i in range(10):
        make_enemy_sprite(i)
    for b in range(3):
        for p in range(3):
            make_boss_sprite(b,p)
    for w in range(8):
        make_bullet_sprite(w)