import pygame, math, random
from constants import *
from projectiles import Projectile, BoomerangProjectile, FlameParticle, RailBeam
from utils import normalize, angle_to

class WeaponSystem:
    def __init__(self, particles):
        self.particles = particles
        self.current = "pistol"
        self.inventory = ["pistol"]
        self.ammo = {k: (v["ammo"] if v["ammo"]>0 else 9999) for k,v in WEAPONS.items()}
        self.fire_timers = {k: 0.0 for k in WEAPONS}
        self.heat = 0.0  # for chain gun

    def switch(self, weapon_name):
        if weapon_name in self.inventory:
            self.current = weapon_name

    def add_weapon(self, name):
        if name not in self.inventory:
            self.inventory.append(name)
            if WEAPONS[name]["ammo"] > 0:
                self.ammo[name] = WEAPONS[name]["ammo"]

    def add_ammo(self, name, amount):
        self.ammo[name] = min(self.ammo[name]+amount, WEAPONS[name]["ammo"] if WEAPONS[name]["ammo"]>0 else 9999)

    def update(self, dt):
        for k in self.fire_timers:
            if self.fire_timers[k] > 0:
                self.fire_timers[k] -= dt
        self.heat = max(0, self.heat-dt*2)

    def can_fire(self):
        w = WEAPONS[self.current]
        if self.fire_timers[self.current] > 0:
            return False
        if self.current != "pistol" and self.ammo.get(self.current,0) <= 0:
            return False
        return True

    def fire(self, px, py, tx, ty, projectiles):
        if not self.can_fire():
            return False
        w = WEAPONS[self.current]
        self.fire_timers[self.current] = w["fire_rate"]
        if self.current != "pistol":
            self.ammo[self.current] = max(0, self.ammo[self.current]-1)

        dx,dy = normalize((tx-px, ty-py))
        spd = 700
        angle = math.atan2(dy,dx)
        color = w["color"]
        wtype = w["type"]

        if wtype == "single":
            p = Projectile(px,py,dx*spd,dy*spd,w["damage"],color,6,False,"player",0,2.0)
            projectiles.append(p)
            self.particles.sparks(px,py,4)

        elif wtype == "pellets":
            for i in range(7):
                spread = random.uniform(-0.25,0.25)
                a = angle+spread
                vx2=math.cos(a)*500; vy2=math.sin(a)*500
                p=Projectile(px,py,vx2,vy2,w["damage"],color,5,False,"player",0,0.6)
                projectiles.append(p)
            self.particles.sparks(px,py,8)

        elif wtype == "pierce":
            p=Projectile(px,py,dx*1000,dy*1000,w["damage"],color,8,True,"player",0,2.0)
            projectiles.append(p)
            self.particles.emit_directional(px,py,angle,0.2,CYAN,6,(200,400))

        elif wtype == "aoe":
            p=Projectile(px,py,dx*400,dy*400,w["damage"],color,10,False,"player",80,2.0)
            projectiles.append(p)
            self.particles.emit(px,py,RED,5,(50,150))

        elif wtype == "chain":
            if self.heat < 3.0:
                spread = random.uniform(-0.1,0.1)
                a=angle+spread
                vx2=math.cos(a)*800; vy2=math.sin(a)*800
                p=Projectile(px,py,vx2,vy2,w["damage"],color,4,False,"player",0,1.0)
                projectiles.append(p)
                self.heat=min(5,self.heat+0.3)
            else:
                return False

        elif wtype == "return":
            vx2=dx*350; vy2=dy*350
            p=BoomerangProjectile(px,py,vx2,vy2,w["damage"],color,"player")
            projectiles.append(p)

        elif wtype == "cone_dot":
            for _ in range(3):
                spread=random.uniform(-0.4,0.4)
                a=angle+spread
                vx2=math.cos(a)*300+random.uniform(-30,30)
                vy2=math.sin(a)*300+random.uniform(-30,30)
                p=FlameParticle(px,py,vx2,vy2)
                projectiles.append(p)

        elif wtype == "rail":
            # Raycast to find endpoint
            step=4; ex=px; ey=py
            for _ in range(500):
                ex+=dx*step; ey+=dy*step
            beam=RailBeam(px,py,ex,ey,w["damage"],color)
            projectiles.append(beam)
            self.particles.emit_directional(px,py,angle,0.1,PURPLE,10,(300,600))

        return True

    def get_current_info(self):
        w=WEAPONS[self.current]
        ammo=self.ammo[self.current] if self.current!="pistol" else -1
        return w["name"], ammo, w["color"]