import pygame, math, random
from constants import *

class Particle:
    __slots__ = ['x','y','vx','vy','color','life','max_life','size','gravity','fade']
    def __init__(self, x, y, vx, vy, color, life, size=4, gravity=0, fade=True):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.color=color; self.life=life; self.max_life=life
        self.size=size; self.gravity=gravity; self.fade=fade

class AfterImage:
    def __init__(self, x, y, surf, alpha):
        self.x=x; self.y=y; self.surf=surf; self.alpha=alpha
        self.timer=0.25

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.afterimages = []

    def emit(self, x, y, color, count=8, speed_range=(50,150), life_range=(0.3,0.8), size=4, gravity=0, spread=math.pi*2):
        for _ in range(count):
            angle = random.uniform(0, spread)
            spd = random.uniform(*speed_range)
            vx = math.cos(angle)*spd
            vy = math.sin(angle)*spd
            life = random.uniform(*life_range)
            sz = random.randint(max(1,size-2), size+2)
            self.particles.append(Particle(x,y,vx,vy,color,life,sz,gravity))

    def emit_directional(self, x, y, angle, spread, color, count=6, speed_range=(80,200), life_range=(0.2,0.5), size=3):
        for _ in range(count):
            a = angle + random.uniform(-spread/2, spread/2)
            spd = random.uniform(*speed_range)
            vx = math.cos(a)*spd
            vy = math.sin(a)*spd
            life = random.uniform(*life_range)
            self.particles.append(Particle(x,y,vx,vy,color,life,size,0))

    def add_afterimage(self, x, y, surf):
        self.afterimages.append(AfterImage(x,y,surf,160))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx*dt
            p.y += p.vy*dt
            p.vy += p.gravity*dt
            p.vx *= 0.95
            alive.append(p)
        self.particles = alive

        ai_alive = []
        for ai in self.afterimages:
            ai.timer -= dt
            ai.alpha -= 400*dt
            if ai.timer > 0 and ai.alpha > 0:
                ai_alive.append(ai)
        self.afterimages = ai_alive

    def draw(self, surf, camera):
        for ai in self.afterimages:
            s = ai.surf.copy()
            s.set_alpha(int(ai.alpha))
            sx, sy = camera.apply(ai.x, ai.y)
            surf.blit(s, (sx - s.get_width()//2, sy - s.get_height()//2))

        for p in self.particles:
            t = p.life/p.max_life
            alpha = int(255*t) if p.fade else 255
            color = (min(255,p.color[0]), min(255,p.color[1]), min(255,p.color[2]))
            sx, sy = camera.apply(p.x, p.y)
            sz = max(1, int(p.size*t))
            if sz <= 2:
                if 0<=sx<surf.get_width() and 0<=sy<surf.get_height():
                    surf.set_at((int(sx),int(sy)), color)
            else:
                tmp = pygame.Surface((sz*2,sz*2), pygame.SRCALPHA)
                pygame.draw.circle(tmp, (*color, alpha), (sz,sz), sz)
                surf.blit(tmp, (sx-sz, sy-sz))

    def explosion(self, x, y, color1, color2, count=30):
        self.emit(x, y, color1, count//2, (100,300), (0.4,1.0), 6, 80)
        self.emit(x, y, color2, count//2, (50,200), (0.3,0.8), 4, 80)
        self.emit(x, y, WHITE, count//4, (200,400), (0.2,0.5), 3, 0)

    def blood(self, x, y, count=12):
        self.emit(x, y, RED, count, (50,200), (0.3,0.7), 4, 150)
        self.emit(x, y, DARK_RED, count//2, (30,120), (0.2,0.5), 3, 150)

    def sparks(self, x, y, count=10):
        self.emit(x, y, YELLOW, count, (100,300), (0.2,0.6), 3, 50)
        self.emit(x, y, WHITE, count//2, (150,350), (0.15,0.4), 2, 50)

    def heal_effect(self, x, y):
        self.emit(x, y, GREEN, 15, (30,100), (0.5,1.2), 5, -60)
        self.emit(x, y, LIME, 8, (20,80), (0.4,1.0), 3, -40)

    def poison_cloud(self, x, y):
        self.emit(x, y, POISON_GREEN, 8, (20,80), (0.8,1.5), 6, -20)

    def ice_shatter(self, x, y):
        self.emit(x, y, ICE_BLUE, 12, (80,250), (0.3,0.8), 5, 100)
        self.emit(x, y, WHITE, 8, (100,300), (0.2,0.6), 3, 100)

    def lava_burst(self, x, y):
        self.emit(x, y, LAVA_ORANGE, 10, (50,180), (0.5,1.2), 5, 60)
        self.emit(x, y, RED, 6, (30,120), (0.4,1.0), 4, 60)