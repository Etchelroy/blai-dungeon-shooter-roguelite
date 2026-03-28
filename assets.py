import pygame
import math
from settings import TILE_PX, TILE_SIZE, TILE_SCALE

_cache = {}

def get_font(size):
    key = ('font', size)
    if key not in _cache:
        try:
            _cache[key] = pygame.font.Font(None, size)
        except:
            _cache[key] = pygame.font.SysFont('monospace', size)
    return _cache[key]

def make_surface(w, h, alpha=True):
    s = pygame.Surface((w, h), pygame.SRCALPHA if alpha else 0)
    s.fill((0,0,0,0) if alpha else (0,0,0))
    return s

def draw_pixel_rect(surf, color, x, y, w, h):
    pygame.draw.rect(surf, color, (x, y, w, h))

def _tile_floor(variant=0):
    s = make_surface(TILE_PX, TILE_PX, False)
    base = [(45,38,52),(50,42,58),(42,36,50)][variant%3]
    s.fill(base)
    import random
    rng = random.Random(variant*7+13)
    for _ in range(18):
        nx = rng.randint(0, TILE_PX-3)
        ny = rng.randint(0, TILE_PX-3)
        shade = rng.randint(-12,12)
        c = tuple(max(0,min(255,base[i]+shade)) for i in range(3))
        pygame.draw.rect(s, c, (nx,ny,rng.randint(2,5),rng.randint(2,5)))
    return s

def _tile_wall(variant=0):
    s = make_surface(TILE_PX, TILE_PX, False)
    bases = [(80,60,90),(70,55,80),(90,70,100)]
    base = bases[variant%3]
    s.fill(base)
    dark = tuple(max(0,b-25) for b in base)
    light = tuple(min(255,b+20) for b in base)
    for row in range(3):
        for col in range(2):
            offset = (col*24 + (row%2)*12) % TILE_PX
            bx = offset
            by = row*16
            pygame.draw.rect(s, dark, (bx, by, 22, 14))
            pygame.draw.rect(s, light, (bx+1, by+1, 20, 2))
    pygame.draw.line(s, dark, (0,0),(TILE_PX-1,0),2)
    pygame.draw.line(s, dark, (0,0),(0,TILE_PX-1),2)
    return s

def _tile_lava(t=0):
    s = make_surface(TILE_PX, TILE_PX, False)
    s.fill((180,40,0))
    for i in range(0,TILE_PX,8):
        for j in range(0,TILE_PX,8):
            v = int(30*math.sin((i+j+t*40)*0.2))
            c = (min(255,210+v), max(0,min(255,60+v)), 0)
            pygame.draw.rect(s,c,(i,j,7,7))
    return s

def _tile_ice(variant=0):
    s = make_surface(TILE_PX, TILE_PX, False)
    s.fill((160,210,240))
    import random
    rng = random.Random(variant+99)
    for _ in range(12):
        x1=rng.randint(0,TILE_PX); y1=rng.randint(0,TILE_PX)
        x2=rng.randint(0,TILE_PX); y2=rng.randint(0,TILE_PX)
        pygame.draw.line(s,(200,230,255),( x1,y1),(x2,y2),1)
    return s

def _tile_spike(active=True):
    s = make_surface(TILE_PX, TILE_PX, False)
    s.fill((55,50,65))
    color = (200,200,220) if active else (80,80,90)
    for i in range(3):
        cx = 8 + i*16
        pts = [(cx,6),(cx-7,TILE_PX-6),(cx+7,TILE_PX-6)]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.polygon(s, (240,240,255) if active else (100,100,110), [(cx,6),(cx-3,22),(cx+3,22)])
    return s

def _tile_poison_vent():
    s = make_surface(TILE_PX, TILE_PX, False)
    s.fill((40,55,40))
    pygame.draw.rect(s,(60,80,60),(8,8,TILE_PX-16,TILE_PX-16))
    for i in range(4):
        x=12+i*8; y=12+i*8
        pygame.draw.circle(s,(80,120,60),(TILE_PX//2,TILE_PX//2),4+i*3,1)
    return s

def _tile_crate():
    s = make_surface(TILE_PX, TILE_PX, True)
    c1=(180,130,60); c2=(140,100,40); c3=(200,160,80)
    s.fill(c1)
    pygame.draw.rect(s,c2,(0,0,TILE_PX,4))
    pygame.draw.rect(s,c2,(0,TILE_PX-4,TILE_PX,4))
    pygame.draw.rect(s,c2,(0,0,4,TILE_PX))
    pygame.draw.rect(s,c2,(TILE_PX-4,0,4,TILE_PX))
    pygame.draw.line(s,c3,(0,TILE_PX//2),(TILE_PX,TILE_PX//2),2)
    pygame.draw.line(s,c3,(TILE_PX//2,0),(TILE_PX//2,TILE_PX),2)
    return s

def get_tile_surface(tile_type, variant=0, t=0):
    key = (tile_type, variant, int(t*4)%4 if tile_type==2 else 0)
    if key in _cache:
        return _cache[key]
    from settings import TILE_FLOOR,TILE_WALL,TILE_LAVA,TILE_ICE,TILE_SPIKE,TILE_POISON_VENT,TILE_CRATE
    if tile_type == TILE_FLOOR:
        s = _tile_floor(variant)
    elif tile_type == TILE_WALL:
        s = _tile_wall(variant)
    elif tile_type == TILE_LAVA:
        s = _tile_lava(t)
    elif tile_type == TILE_ICE:
        s = _tile_ice(variant)
    elif tile_type == TILE_SPIKE:
        s = _tile_spike(variant==0)
    elif tile_type == TILE_POISON_VENT:
        s = _tile_poison_vent()
    elif tile_type == TILE_CRATE:
        s = _tile_crate()
    else:
        s = _tile_floor(variant)
    _cache[key] = s
    return s

def draw_player_sprite(surf, x, y, angle, dash_alpha=255, frame=0):
    s = make_surface(36, 36)
    body_color = (80,160,220)
    dark = (50,110,170)
    eye = (255,255,100)
    cx, cy = 18, 20
    pygame.draw.circle(s, dark, (cx,cy), 14)
    pygame.draw.circle(s, body_color, (cx,cy), 12)
    pygame.draw.rect(s, dark, (cx-5,cy-2,10,14))
    ex = int(cx + 7*math.cos(angle))
    ey = int(cy + 7*math.sin(angle))
    pygame.draw.circle(s, eye, (ex,ey), 4)
    pygame.draw.circle(s, (255,255,255), (ex+1,ey-1), 1)
    if dash_alpha < 255:
        s.set_alpha(dash_alpha)
    surf.blit(s, (x-18, y-18))

def draw_enemy_sprite(surf, x, y, etype, frame=0, hp_ratio=1.0):
    sprites = {
        'grunt': _draw_grunt,
        'runner': _draw_runner,
        'tank': _draw_tank,
        'shooter': _draw_shooter,
        'bomber': _draw_bomber,
        'shielder': _draw_shielder,
        'sniper': _draw_sniper_enemy,
        'summoner': _draw_summoner,
        'phantom': _draw_phantom,
        'berserker': _draw_berserker,
    }
    fn = sprites.get(etype, _draw_grunt)
    fn(surf, x, y, frame, hp_ratio)

def _draw_grunt(surf, x, y, frame, hp_ratio):
    s = make_surface(32,32)
    bob = int(2*math.sin(frame*0.3))
    pygame.draw.circle(s,(180,60,60),(16,14+bob),10)
    pygame.draw.rect(s,(140,40,40),(10,22+bob,12,8))
    pygame.draw.circle(s,(220,180,140),(16,14+bob),6)
    pygame.draw.circle(s,(50,20,20),(13,12+bob),2)
    pygame.draw.circle(s,(50,20,20),(19,12+bob),2)
    surf.blit(s,(x-16,y-16))

def _draw_runner(surf, x, y, frame, hp_ratio):
    s = make_surface(28,28)
    bob = int(3*math.sin(frame*0.5))
    pygame.draw.circle(s,(80,200,80),(14,12+bob),8)
    pygame.draw.rect(s,(50,160,50),(8,18+bob,14,6))
    leg_off = int(4*math.sin(frame*0.5))
    pygame.draw.line(s,(50,160,50),(10,24+bob),(8,28+bob+leg_off),2)
    pygame.draw.line(s,(50,160,50),(18,24+bob),(20,28+bob-leg_off),2)
    surf.blit(s,(x-14,y-14))

def _draw_tank(surf, x, y, frame, hp_ratio):
    s = make_surface(44,44)
    pygame.draw.rect(s,(100,100,140),(6,8,32,28))
    pygame.draw.circle(s,(120,120,160),(22,20),14)
    pygame.draw.rect(s,(160,160,200),(10,6,24,8))
    pygame.draw.circle(s,(60,60,80),(22,20),6)
    surf.blit(s,(x-22,y-22))

def _draw_shooter(surf, x, y, frame, hp_ratio):
    s = make_surface(32,32)
    bob = int(math.sin(frame*0.2)*2)
    pygame.draw.circle(s,(180,120,220),(16,14+bob),9)
    pygame.draw.rect(s,(22,24,TILE_PX),(13,22+bob,6,8))
    pygame.draw.rect(s,(200,150,240),(20,18+bob,12,4))
    pygame.draw.circle(s,(255,200,100),(16,14+bob),4)
    surf.blit(s,(x-16,y-16))

def _draw_bomber(surf, x, y, frame, hp_ratio):
    s = make_surface(34,34)
    pulse = int(3*math.sin(frame*0.4))
    pygame.draw.circle(s,(220,140,30),(17,17),11+pulse//2)
    pygame.draw.circle(s,(255,200,50),(17,17),7)
    pygame.draw.line(s,(200,100,20),(17,6),(17,0),3)
    pygame.draw.circle(s,(255,255,0),(17,0),3)
    surf.blit(s,(x-17,y-17))

def _draw_shielder(surf, x, y, frame, hp_ratio):
    s = make_surface(38,38)
    pygame.draw.circle(s,(80,80,180),(19,19),13)
    pygame.draw.arc(s,(150,180,255),pygame.Rect(4,4,30,30),0.5,2.6,5)
    pygame.draw.rect(s,(100,100,200),(14,24,10,10))
    surf.blit(s,(x-19,y-19))

def _draw_sniper_enemy(surf, x, y, frame, hp_ratio):
    s = make_surface(30,30)
    bob = int(math.sin(frame*0.15)*1)
    pygame.draw.circle(s,(60,180,180),(15,14+bob),9)
    pygame.draw.rect(s,(40,140,140),(11,22+bob,8,7))
    pygame.draw.rect(s,(80,220,220),(20,18+bob,14,3))
    surf.blit(s,(x-15,y-15))

def _draw_summoner(surf, x, y, frame, hp_ratio):
    s = make_surface(36,36)
    angle = frame*0.05
    for i in range(4):
        a = angle + i*math.pi/2
        ox=int(12*math.cos(a)); oy=int(12*math.sin(a))
        pygame.draw.circle(s,(180,80,220),(18+ox,18+oy),4)
    pygame.draw.circle(s,(130,50,180),(18,18),10)
    pygame.draw.circle(s,(200,150,255),(18,18),5)
    surf.blit(s,(x-18,y-18))

def _draw_phantom(surf, x, y, frame, hp_ratio):
    s = make_surface(32,32)
    alpha = int(120 + 80*math.sin(frame*0.1))
    pygame.draw.circle(s,(100,100,220,alpha),(16,14),10)
    pygame.draw.circle(s,(150,150,255,alpha),(16,14),6)
    for i in range(3):
        x2=10+i*6; y2=22
        pygame.draw.line(s,(100,100,200,alpha),(x2,y2),(x2,26+int(3*math.sin(frame*0.2+i))),2)
    s.set_alpha(alpha)
    surf.blit(s,(x-16,y-16))

def _draw_berserker(surf, x, y, frame, hp_ratio):
    s = make_surface(40,40)
    rage = 1.0 - hp_ratio
    r = int(160+95*rage); g = int(40-20*rage)
    pygame.draw.circle(s,(r,g,20),(20,18),14)
    pygame.draw.rect(s,(r-20,g,10),(12,30,16,8))
    for i in [-1,1]:
        pygame.draw.line(s,(r,g,20),(20,10),(20+i*12,4),3)
    pygame.draw.circle(s,(255,100,0),(20,18),5)
    surf.blit(s,(x-20,y-20))

def draw_boss_sprite(surf, x, y, boss_type, phase, frame, hp_ratio):
    if boss_type == 0:
        _draw_boss_inferno(surf, x, y, phase, frame, hp_ratio)
    elif boss_type == 1:
        _draw_boss_titan(surf, x, y, phase, frame, hp_ratio)
    else:
        _draw_boss_void(surf, x, y, phase, frame, hp_ratio)

def _draw_boss_inferno(surf, x, y, phase, frame, hp_ratio):
    s = make_surface(80,80)
    flicker = int(5*math.sin(frame*0.3))
    colors = [(220,80,20),(255,120,0),(255,200,50)]
    c = colors[min(phase,2)]
    pygame.draw.circle(s,c,(40,40),28+flicker//2)
    pygame.draw.circle(s,(255,220,100),(40,40),16)
    pygame.draw.circle(s,(255,255,200),(40,40),8)
    for i in range(6):
        a=frame*0.04+i*math.pi/3
        ex=int(40+26*math.cos(a)); ey=int(40+26*math.sin(a))
        pygame.draw.circle(s,colors[min(phase,2)],(ex,ey),4+flicker)
    surf.blit(s,(x-40,y-40))

def _draw_boss_titan(surf, x, y, phase, frame, hp_ratio):
    s = make_surface(100,100)
    colors = [(80,80,160),(100,100,180),(140,140,220)]
    c = colors[min(phase,2)]
    pygame.draw.rect(s,c,(20,20,60,60))
    pygame.draw.circle(s,tuple(min(255,v+40) for v in c),(50,30),22)
    arm_ang = math.sin(frame*0.05)*0.4
    for side in [-1,1]:
        ax=50+side*32; ay=50
        pygame.draw.line(s,c,(50+side*18,40),(ax,ay),8)
        pygame.draw.rect(s,tuple(v+20 for v in c),(ax-8,ay-8,16,16))
    surf.blit(s,(x-50,y-50))

def _draw_boss_void(surf, x, y, phase, frame, hp_ratio):
    s = make_surface(90,90)
    colors = [(50,0,100),(80,0,150),(120,0,220)]
    c = colors[min(phase,2)]
    angle = frame*0.03
    for i in range(5):
        a = angle+i*2*math.pi/5
        r_out=38; r_in=20
        ox=int(45+r_out*math.cos(a)); oy=int(45+r_out*math.sin(a))
        ix=int(45+r_in*math.cos(a+0.5)); iy=int(45+r_in*math.sin(a+0.5))
        pygame.draw.line(s,c,(45,45),(ox,oy),3)
        pygame.draw.circle(s,tuple(min(255,v+80) for v in c),(ox,oy),6)
    pygame.draw.circle(s,(20,0,40),(45,45),18)
    pygame.draw.circle(s,c,(45,45),12)
    pygame.draw.circle(s,(180,0,255),(45,45),5)
    surf.blit(s,(x-45,y-45))

def draw_projectile_sprite(surf, x, y, ptype, angle=0, frame=0):
    if ptype == 'bullet':
        pygame.draw.circle(surf,(255,220,100),(x,y),4)
        pygame.draw.circle(surf,(255,255,200),(x,y),2)
    elif ptype == 'pellet':
        pygame.draw.circle(surf,(255,160,0),(x,y),3)
    elif ptype == 'plasma':
        pygame.draw.circle(surf,(100,200,255),(x,y),6)
        pygame.draw.circle(surf,(200,240,255),(x,y),3)
    elif ptype == 'sniper':
        ex=int(x+12*math.cos(angle)); ey=int(y+12*math.sin(angle))
        pygame.draw.line(surf,(200,255,255),(x,y),(ex,ey),3)
        pygame.draw.circle(surf,(255,255,255),(x,y),3)
    elif ptype == 'flame':
        r=int(4+3*math.sin(frame*0.5))
        pygame.draw.circle(surf,(255,120,0),(x,y),r)
        pygame.draw.circle(surf,(255,200,0),(x,y),r//2)
    elif ptype == 'chain':
        pygame.draw.circle(surf,(100,255,200),(x,y),5)
        pygame.draw.circle(surf,(200,255,240),(x,y),2)
    elif ptype == 'boomerang':
        s=make_surface(20,8)
        pygame.draw.ellipse(s,(200,160,80),(0,0,20,8))
        rs=pygame.transform.rotate(s, math.degrees(-angle))
        surf.blit(rs,(x-rs.get_width()//2,y-rs.get_height()//2))
    elif ptype == 'enemy_bullet':
        pygame.draw.circle(surf,(220,60,60),(x,y),4)
        pygame.draw.circle(surf,(255,120,120),(x,y),2)
    elif ptype == 'grenade':
        pygame.draw.circle(surf,(80,180,80),(x,y),5)
        pygame.draw.circle(surf,(120,220,120),(x,y),2)
    else:
        pygame.draw.circle(surf,(255,255,255),(x,y),3)