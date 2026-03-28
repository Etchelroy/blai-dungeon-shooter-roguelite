import pygame, math, random
from constants import *
from utils import normalize, dist

class Projectile:
    def __init__(self, x, y, vx, vy, damage, color, size=6, piercing=False, owner="player",
                 aoe_radius=0, lifetime=3.0, homing=False, homing_target=None):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.damage=damage; self.color=color; self.size=size
        self.piercing=piercing; self.owner=owner
        self.aoe_radius=aoe_radius; self.lifetime=lifetime
        self.homing=homing; self.homing_target=homing_target
        self.alive=True
        self.hit_enemies=set()
        self.trail=[]

    def update(self, dt, walls, enemies=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return

        if self.homing and enemies:
            best = None; best_d = 300
            for e in enemies:
                d = dist((self.x,self.y),(e.x,e.y))
                if d < best_d and e.alive:
                    best_d=d; best=e
            if best:
                dx,dy = normalize((best.x-self.x, best.y-self.y))
                spd = math.hypot(self.vx,self.vy)
                self.vx += dx*spd*dt*3
                self.vy += dy*spd*dt*3
                l = math.hypot(self.vx,self.vy)
                if l>0: self.vx=self.vx/l*spd; self.vy=self.vy/l*spd

        self.trail.append((self.x,self.y))
        if len(self.trail)>8: self.trail.pop(0)

        self.x += self.vx*dt
        self.y += self.vy*dt

        for wall in walls:
            if wall.collidepoint(self.x, self.y):
                self.alive = False
                return

    def draw(self, surf, camera):
        if not self.alive: return
        for i,pos in enumerate(self.trail):
            alpha = int(120*(i/max(1,len(self.trail))))
            sx,sy = camera.apply(*pos)
            sz = max(1, int(self.size*(i/max(1,len(self.trail)))))
            if sz > 0:
                tmp = pygame.Surface((sz*2+1,sz*2+1),pygame.SRCALPHA)
                pygame.draw.circle(tmp, (*self.color, alpha), (sz,sz), sz)
                surf.blit(tmp,(sx-sz,sy-sz))
        sx,sy = camera.apply(self.x,self.y)
        pygame.draw.circle(surf, self.color, (int(sx),int(sy)), self.size)
        pygame.draw.circle(surf, WHITE, (int(sx),int(sy)), max(1,self.size-2))

class BoomerangProjectile:
    def __init__(self, x, y, vx, vy, damage, color, owner="player"):
        self.x=x; self.y=y; self.ox=x; self.oy=y
        self.vx=vx; self.vy=vy; self.damage=damage; self.color=color
        self.owner=owner; self.alive=True; self.returning=False
        self.lifetime=2.5; self.hit_enemies=set()
        self.size=10; self.angle=0

    def update(self, dt, walls, player=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive=False; return

        if not self.returning:
            d = dist((self.x,self.y),(self.ox,self.oy))
            if d > 250:
                self.returning=True

        if self.returning and player:
            dx,dy = normalize((player.x-self.x, player.y-self.y))
            spd = math.hypot(self.vx,self.vy)
            self.vx = dx*max(spd,300)
            self.vy = dy*max(spd,300)
            if dist((self.x,self.y),(player.x,player.y)) < 20:
                self.alive=False; return
        else:
            self.vx *= 0.99; self.vy *= 0.99

        self.x += self.vx*dt
        self.y += self.vy*dt
        self.angle += 360*dt

        for wall in walls:
            if wall.collidepoint(self.x,self.y):
                self.returning=True

    def draw(self, surf, camera):
        if not self.alive: return
        sx,sy = camera.apply(self.x,self.y)
        tmp = pygame.Surface((24,24), pygame.SRCALPHA)
        pygame.draw.arc(tmp, self.color, (2,2,20,20), 0, math.pi*1.5, 4)
        rotated = pygame.transform.rotate(tmp, self.angle)
        surf.blit(rotated, (int(sx)-rotated.get_width()//2, int(sy)-rotated.get_height()//2))

class FlameParticle:
    def __init__(self, x, y, vx, vy):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy
        self.lifetime=random.uniform(0.3,0.7)
        self.max_life=self.lifetime; self.alive=True
        self.damage_tick=0.0; self.size=random.randint(6,12)
        self.hit_enemies=set()
        self.owner="player"
        self.aoe_radius=0; self.piercing=True

    def update(self, dt, walls, enemies=None):
        self.lifetime-=dt
        if self.lifetime<=0: self.alive=False; return
        self.x+=self.vx*dt; self.y+=self.vy*dt
        self.vx*=0.92; self.vy*=0.92

    def draw(self, surf, camera):
        if not self.alive: return
        t=self.lifetime/self.max_life
        r=min(255,int(255))
        g=min(255,int(160*t))
        b=0
        sx,sy=camera.apply(self.x,self.y)
        sz=max(2,int(self.size*t))
        tmp=pygame.Surface((sz*2,sz*2),pygame.SRCALPHA)
        pygame.draw.circle(tmp,(r,g,b,int(200*t)),(sz,sz),sz)
        surf.blit(tmp,(int(sx)-sz,int(sy)-sz))

class RailBeam:
    def __init__(self, x1, y1, x2, y2, damage, color=PURPLE):
        self.x1=x1;self.y1=y1;self.x2=x2;self.y2=y2
        self.damage=damage;self.color=color
        self.lifetime=0.2;self.alive=True
        self.owner="player";self.aoe_radius=0
        self.piercing=True;self.hit_enemies=set()
        self.size=4
        self.x=x1;self.y=y1;self.vx=0;self.vy=0

    def update(self, dt, walls, enemies=None):
        self.lifetime-=dt
        if self.lifetime<=0: self.alive=False

    def draw(self, surf, camera):
        if not self.alive: return
        sx1,sy1=camera.apply(self.x1,self.y1)
        sx2,sy2=camera.apply(self.x2,self.y2)
        pygame.draw.line(surf,WHITE,(int(sx1),int(sy1)),(int(sx2),int(sy2)),6)
        pygame.draw.line(surf,self.color,(int(sx1),int(sy1)),(int(sx2),int(sy2)),3)

class EnemyProjectile:
    def __init__(self, x, y, vx, vy, damage, color=RED, size=7):
        self.x=x;self.y=y;self.vx=vx;self.vy=vy
        self.damage=damage;self.color=color;self.size=size
        self.alive=True;self.lifetime=4.0;self.owner="enemy"
        self.aoe_radius=0;self.piercing=False;self.hit_enemies=set()

    def update(self, dt, walls, enemies=None):
        self.lifetime-=dt
        if self.lifetime<=0: self.alive=False; return
        self.x+=self.vx*dt; self.y+=self.vy*dt
        for wall in walls:
            if wall.collidepoint(self.x,self.y):
                self.alive=False; return

    def draw(self, surf, camera):
        if not self.alive: return
        sx,sy=camera.apply(self.x,self.y)
        pygame.draw.circle(surf,self.color,(int(sx),int(sy)),self.size)