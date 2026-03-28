import pygame, math, random
from settings import *
from src.utils import angle_to, distance
from src.particles import ParticleSystem

class Boss:
    def __init__(self, btype, x, y, particles, wave):
        self.btype = btype
        self.x, self.y = float(x), float(y)
        self.particles = particles
        self.wave = wave
        self.phase = 1
        self.alive = True
        self.vx = self.vy = 0.0
        self.anim_t = 0.0
        self.flash_t = 0.0
        self.attack_cd = 0.0
        self.move_cd = 0.0
        self.move_target = (x, y)
        self.vulnerable = False
        self.vuln_timer = 0.0
        self.phase_transition = False
        self.transition_timer = 0.0
        self.death_done = False
        self.death_timer = 0.0
        self.projectiles = []
        self.summons = []
        self._setup()

    def _setup(self):
        configs = {
            'guardian': {'hp':800,  'size':56, 'col':(120,60,200),  'name':'THE GUARDIAN'},
            'inferno':  {'hp':1000, 'size':64, 'col':(255,100,20),  'name':'INFERNO KING'},
            'void':     {'hp':1200, 'size':72, 'col':(40,20,80),    'name':'VOID HERALD'},
        }
        c = configs[self.btype]
        self.hp = c['hp']
        self.max_hp = c['hp']
        self.size = c['size']
        self.col = c['col']
        self.name = c['name']
        self.phase2_hp = c['hp'] * 0.66
        self.phase3_hp = c['hp'] * 0.33
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def get_center(self):
        return (self.x + self.size/2, self.y + self.size/2)

    def take_damage(self, amt):
        if not self.vulnerable and not self.phase_transition:
            return 0
        self.hp -= amt
        self.flash_t = 0.08
        if self.hp <= 0:
            self.hp = 0
            if not self.death_done:
                self.alive = False
                self.death_timer = 2.0
        return amt

    def check_phase(self):
        if self.phase == 1 and self.hp <= self.phase2_hp:
            self.phase = 2
            self.phase_transition = True
            self.transition_timer = 2.0
            self.vulnerable = False
            return True
        if self.phase == 2 and self.hp <= self.phase3_hp:
            self.phase = 3
            self.phase_transition = True
            self.transition_timer = 2.0
            self.vulnerable = False
            return True
        return False

    def update(self, dt, player, arena):
        self.anim_t += dt
        if self.flash_t > 0: self.flash_t -= dt

        if self.phase_transition:
            self.transition_timer -= dt
            self._spawn_transition_particles()
            if self.transition_timer <= 0:
                self.phase_transition = False
                self.vulnerable = True
                self.vuln_timer = 5.0
            return

        if self.vuln_timer > 0:
            self.vuln_timer -= dt
            if self.vuln_timer <= 0:
                self.vulnerable = False

        self.attack_cd -= dt
        self.move_cd -= dt

        px, py = player.get_center()
        bx, by = self.get_center()

        if self.move_cd <= 0:
            self.move_cd = random.uniform(1.5, 3.0)
            if self.btype == 'guardian':
                self.move_target = (px + random.uniform(-100,100), py + random.uniform(-100,100))
            elif self.btype == 'inferno':
                ang = random.uniform(0, math.pi*2)
                r = random.uniform(100, 250)
                self.move_target = (px + math.cos(ang)*r, py + math.sin(ang)*r)
            elif self.btype == 'void':
                self.move_target = (px, py)

        # move toward target
        tx, ty = self.move_target
        dx, dy = tx - self.x, ty - self.y
        d = max(1, math.sqrt(dx*dx+dy*dy))
        spd = 80 + self.phase * 30
        self.vx = (dx/d) * spd
        self.vy = (dy/d) * spd

        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt
        if arena and arena.is_walkable_rect(pygame.Rect(nx, self.y, self.size, self.size)):
            self.x = nx
        if arena and arena.is_walkable_rect(pygame.Rect(self.x, ny, self.size, self.size)):
            self.y = ny

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.attack_cd <= 0:
            self._attack(player)
            self.attack_cd = max(0.8, 2.5 - self.phase * 0.5)

        # update projectiles
        for p in self.projectiles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.projectiles = [p for p in self.projectiles if p['life'] > 0]

        self.check_phase()

    def _spawn_transition_particles(self):
        cx, cy = self.get_center()
        for _ in range(3):
            ang = random.uniform(0, math.pi*2)
            spd = random.uniform(80, 200)
            self.particles.emit(cx, cy, color=self.col,
                vx=math.cos(ang)*spd, vy=math.sin(ang)*spd,
                life=random.uniform(0.5, 1.2), size=random.randint(4, 10))

    def _attack(self, player):
        cx, cy = self.get_center()
        px, py = player.get_center()
        ang = angle_to(cx, cy, px, py)

        if self.btype == 'guardian':
            if self.phase == 1:
                self._shoot_spread(cx, cy, ang, 3, 0.3)
            elif self.phase == 2:
                self._shoot_spread(cx, cy, ang, 5, 0.25)
                self.vulnerable = True; self.vuln_timer = 2.0
            else:
                self._shoot_circle(cx, cy, 8)
                self.vulnerable = True; self.vuln_timer = 1.5

        elif self.btype == 'inferno':
            if self.phase == 1:
                self._shoot_spiral(cx, cy, 4)
            elif self.phase == 2:
                self._shoot_spiral(cx, cy, 8)
                self.vulnerable = True; self.vuln_timer = 2.0
            else:
                self._shoot_spiral(cx, cy, 12)
                self._shoot_spread(cx, cy, ang, 3, 0.4)
                self.vulnerable = True; self.vuln_timer = 1.5

        elif self.btype == 'void':
            if self.phase == 1:
                self._shoot_spread(cx, cy, ang, 5, 0.2)
            elif self.phase == 2:
                self._shoot_circle(cx, cy, 6)
                self._shoot_spread(cx, cy, ang, 3, 0.3)
                self.vulnerable = True; self.vuln_timer = 2.0
            else