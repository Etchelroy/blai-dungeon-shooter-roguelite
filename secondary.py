import pygame, math, random
from constants import *
from particles import ParticleSystem
from projectiles import EnemyProjectile
from utils import normalize, dist

class SecondarySystem:
    def __init__(self, particles):
        self.particles = particles
        self.abilities = ["shield","grenade","heal","turret","decoy","emp"]
        self.current_idx = 0
        self.cooldowns = {a:0.0 for a in self.abilities}
        self.max_cooldowns = {
            "shield":  8.0,
            "grenade": 4.0,
            "heal":    10.0,
            "turret":  15.0,
            "decoy":   12.0,
            "emp":     20.0,
        }
        self.active_effects = []  # list of dicts
        self.shield_active = False
        self.shield_timer = 0.0
        self.shield_hp = 0

    @property
    def current(self):
        return self.abilities[self.current_idx]

    def next(self):
        self.current_idx = (self.current_idx+1) % len(self.abilities)

    def prev(self):
        self.current_idx = (self.current_idx-1) % len(self.abilities)

    def can_use(self):
        return self.cooldowns[self.current] <= 0

    def update(self, dt, player, enemies, projectiles):
        for a in self.abilities:
            if self.cooldowns[a] > 0:
                self.cooldowns[a] = max(0, self.cooldowns[a]-dt)

        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0 or self.shield_hp <= 0:
                self.shield_active = False

        alive_effects = []
        for eff in self.active_effects:
            eff['timer'] -= dt
            if eff['timer'] <= 0:
                continue
            if eff['type'] == 'turret':
                eff['fire_timer'] -= dt
                if eff['fire_timer'] <= 0:
                    eff['fire_timer'] = 0.8
                    if enemies:
                        target = min(enemies, key=lambda e: dist((eff['x'],eff['y']),(e.x,e.y)) if e.alive else 9999)
                        if dist((eff['x'],eff['y']),(target.x,target.y)) < 400 and target.alive:
                            dx,dy = normalize((target.x-eff['x'], target.y-eff['y']))
                            ep = EnemyProjectile(eff['x'],eff['y'],dx*500,dy*500,20,(0,200,255),7)
                            ep.owner="player"
                            projectiles.append(ep)
                self.particles.sparks(eff['x']+random.uniform(-5,5), eff['y'], 1)
            elif eff['type'] == 'decoy':
                # Decoy attracts nearby enemies
                for e in enemies:
                    if e.alive and dist((e.x,e.y),(eff['x'],eff['y'])) < 200:
                        dx,dy = normalize((eff['x']-e.x, eff['y']-e.y))
                        e.x += dx*30*dt
                        e.y += dy*30*dt
                if random.random() < 0.3:
                    self.particles.emit(eff['x'],eff['y'],(200,200,50),2,(20,60),(0.2,0.5),3)
            alive_effects.append(eff)
        self.active_effects = alive_effects

    def use(self, player, enemies, projectiles, camera):
        if not self.can_use(): return False
        ability = self.current
        self.cooldowns[ability] = self.max_cooldowns[ability]

        if ability == "shield":
            self.shield_active = True
            self.shield_timer = 4.0
            self.shield_hp = 80
            self.particles.emit(player.x,player.y,(100,150,255),20,(30,100),(0.5,1.0),5)
            return True

        elif ability == "grenade":
            # Drop grenade that explodes after 1s
            mx,my = pygame.mouse.get_pos()
            wx,wy = camera.screen_to_world(mx,my)
            self.active_effects.append({
                'type':'grenade','x':wx,'y':wy,'timer':1.0,
                'damage':80,'radius':120,'exploded':False
            })
            return True

        elif ability == "heal":
            heal = 40
            player.hp = min(player.max_hp, player.hp+heal)
            self.particles.heal_effect(player.x, player.y)
            return True

        elif ability == "turret":
            self.active_effects.append({
                'type':'turret','x':player.x,'y':player.y-30,
                'timer':10.0,'fire_timer':0.0
            })
            return True

        elif ability == "decoy":
            self.active_effects.append({
                'type':'decoy','x':player.x+random.uniform(-100,100),
                'y':player.y+random.uniform(-100,100),'timer':8.0
            })
            return True

        elif ability == "emp":
            camera.shake(12, 0.5)
            for e in enemies:
                if dist((e.x,e.y),(player.x,player.y)) < 300 and e.alive:
                    e.stunned = 3.0
                    e.hp -= 20
            for p in projectiles:
                if hasattr(p,'owner') and p.owner=="enemy":
                    px2,py2=p.x,p.y
                    if dist((px2,py2),(player.x,player.y)) < 300:
                        p.alive=False
            self.particles.explosion(player.x,player.y,CYAN,BLUE,40)
            return True

        return False

    def process_grenades