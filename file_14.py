import pygame, math, random
from settings import *
from src.utils import clamp, angle_to, distance, lerp
from src.particles import ParticleSystem

ENEMY_DEFS = {
    'grunt':     {'hp':40,  'spd':80,  'dmg':10, 'score':100, 'tier':1, 'col':(200,60,60),   'size':20},
    'runner':    {'hp':25,  'spd':140, 'dmg':8,  'score':120, 'tier':1, 'col':(220,120,40),  'size':16},
    'shielder':  {'hp':80,  'spd':55,  'dmg':15, 'score':150, 'tier':1, 'col':(100,100,200), 'size':22},
    'shooter':   {'hp':35,  'spd':60,  'dmg':12, 'score':130, 'tier':2, 'col':(200,60,180),  'size':18},
    'bomber':    {'hp':50,  'spd':90,  'dmg':30, 'score':180, 'tier':2, 'col':(230,180,40),  'size':20},
    'healer':    {'hp':45,  'spd':70,  'dmg':8,  'score':200, 'tier':2, 'col':(60,200,120),  'size':18},
    'tank':      {'hp':200, 'spd':40,  'dmg':25, 'score':300, 'tier':2, 'col':(140,60,60),   'size':28},
    'ghost':     {'hp':30,  'spd':100, 'dmg':15, 'score':250, 'tier':3, 'col':(180,180,255), 'size':20},
    'splitter':  {'hp':60,  'spd':75,  'dmg':12, 'score':220, 'tier':2, 'col':(200,100,200), 'size':22},
    'berserker': {'hp':90,  'spd':110, 'dmg':20, 'score':280, 'tier':3, 'col':(255,40,40),   'size':24},
}

class Enemy(pygame.sprite.Sprite):
    def __init__(self, etype, x, y, particles):
        super().__init__()
        self.etype = etype
        d = ENEMY_DEFS[etype]
        self.hp = d['hp']
        self.max_hp = d['hp']
        self.spd = d['spd']
        self.dmg = d['dmg']
        self.score = d['score']
        self.tier = d['tier']
        self.col = d['col']
        self.size = d['size']
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.alive = True
        self.particles = particles
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.anim_t = random.uniform(0, 6.28)
        self.state = 'idle'
        self.state_timer = 0.0
        self.shoot_cd = 0.0
        self.aggro = False
        self.shield_hp = 30 if etype == 'shielder' else 0
        self.phase = 1
        self.flash_t = 0.0
        self.death_particles_spawned = False
        self.stun_t = 0.0
        self.poison_t = 0.0
        self.burn_t = 0.0
        self.slow_t = 0.0
        self.heal_cd = 0.0

    def get_center(self):
        return (self.x + self.size/2, self.y + self.size/2)

    def take_damage(self, amt, dtype='bullet'):
        if self.shield_hp > 0 and dtype != 'pierce':
            self.shield_hp -= amt
            if self.shield_hp < 0: self.shield_hp = 0
            self.flash_t = 0.1
            return 0
        self.hp -= amt
        self.flash_t = 0.1
        self.aggro = True
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return amt

    def apply_status(self, status, duration):
        if status == 'stun': self.stun_t = max(self.stun_t, duration)
        elif status == 'poison': self.poison_t = max(self.poison_t, duration)
        elif status == 'burn': self.burn_t = max(self.burn_t, duration)
        elif status == 'slow': self.slow_t = max(self.slow_t, duration)

    def update(self, dt, player, arena, enemies):
        if not self.alive: return
        self.anim_t += dt * 3
        if self.flash_t > 0: self.flash_t -= dt
        if self.stun_t > 0:
            self.stun_t -= dt
            return
        if self.poison_t > 0:
            self.poison_t -= dt
            self.take_damage(5 * dt)
        if self.burn_t > 0:
            self.burn_t -= dt
            self.take_damage(8 * dt)
        if self.slow_t > 0: self.slow_t -= dt

        spd_mult = 0.5 if self.slow_t > 0 else 1.0

        px, py = player.get_center()
        ex, ey = self.get_center()
        dist = distance(ex, ey, px, py)
        ang = angle_to(ex, ey, px, py)

        if dist < AGGRO_RANGE:
            self.aggro = True

        if self.aggro:
            self._ai(dt, player, arena, enemies, dist, ang, spd_mult)

        self._move(dt, arena)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def _ai(self, dt, player, arena, enemies, dist, ang, spd_mult):
        px, py = player.get_center()
        ex, ey = self.get_center()

        if self.etype == 'grunt':
            self._chase(ang, spd_mult)
        elif self.etype == 'runner':
            self._chase(ang, spd_mult * 1.2)
            if dist < 60:
                self._flee(ang, spd_mult)
        elif self.etype == 'shielder':
            self._chase(ang, spd_mult * 0.8)
        elif self.etype == 'shooter':
            if dist > 200:
                self._chase(ang, spd_mult * 0.8)
            else:
                self._strafe(ang, spd_mult)
            self.shoot_cd -= 0.016
            if self.shoot_cd <= 0:
                self.shoot_cd = 2.0
                self._shoot_bullet(player)
        elif self.etype == 'bomber':
            if dist > 80:
                self._chase(ang, spd_mult)
            else:
                self._explode_death = True
        elif self.etype == 'healer':
            self._heal_nearby(enemies, dt)
            self._flee(ang, spd_mult)
        elif self.etype == 'tank':
            self._chase(ang, spd_mult * 0.6)
        elif self.etype == 'ghost':
            # phases through walls
            self.vx = math.cos(ang) * self.spd * spd_mult
            self.vy = math.sin(ang) * self.spd * spd_mult
        elif self.etype == 'splitter':
            self._chase(ang, spd_mult)
        elif self.etype == 'berserker':
            mult = 1.0 + (1.0 - self.hp/self.max_hp) * 1.5
            self._chase(ang, spd_mult * mult)

    def _chase(self, ang, mult=1.0):
        self.vx = math.cos(ang) * self.spd * mult
        self.vy = math.sin(ang) * self.spd * mult

    def _flee(self, ang, mult=1.0):
        self.vx = -math.cos(ang) * self.spd * mult
        self.vy = -math.sin(ang) * self.spd * mult

    def _strafe(self, ang, mult=1.0):
        perp = ang + math.pi/2 + math.sin(self.anim_t) * 0.3
        self.vx = math.cos(perp) * self.spd * mult
        self.vy = math.sin(perp) * self.spd * mult

    def _heal_nearby(self, enemies, dt):
        self.heal_cd -= dt
        if self.heal_cd <= 0:
            self.heal_cd = 3.0
            for e in enemies:
                if e is not self and e.alive:
                    d = distance(self.x, self.y, e.x, e.y)
                    if d < 150:
                        e.hp = min(e.max_hp, e.hp + 20)

    def _shoot_bullet(self, player):
        # signal via return; handled in game
        pass

    def _move(self, dt, arena):
        if self.etype == 'ghost':
            self.x += self.vx * dt
            self.y += self.vy * dt
            return
        nx = self.x + self.vx * dt
        ny = self.y + self.vy * dt
        r = pygame.Rect(nx, self.y, self.size, self.size)
        if arena and not arena.is_walkable_rect(r):
            self.vx *= -0.5; nx = self.x
        r = pygame.Rect(self.x, ny, self.size, self.size)
        if arena and not arena.is_walkable_rect(r):
            self.vy *= -0.5; ny = self.y
        self.x = nx; self.y = ny
        self.vx *= 0.85; self.vy *= 0.85

    def spawn_death_particles(self):
        if self.death_particles_spawned: return
        self.death_particles_spawned = True
        cx, cy = self.get_center()
        for _ in range(20):
            ang = random.uniform(0, math.pi*2)
            spd = random.uniform(60, 180)
            self.particles.emit(cx, cy,
                color=self.col,
                vx=math.cos(ang)*spd, vy=math.sin(ang)*spd,
                life=random.uniform(0.4, 0.9),
                size=random.randint(3, 7))
        if self.etype == 'splitter':
            return True  # signal to spawn children
        return False

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        s = self.size
        col = (255, 255, 255) if self.flash_t > 0 else self.col

        # base body
        pygame.draw.rect(surf, col, (sx, sy, s, s))

        # type-specific details
        if self.etype == 'shielder' and self.shield_hp > 0:
            pygame.draw.rect(surf, (100, 150, 255), (sx-2, sy-2, s+4, s+4), 3)
        if self.etype == 'ghost':
            body = pygame.Surface((s, s), pygame.SRCALPHA)
            body.fill((*col, 140))
            surf.blit(body, (sx, sy))
        if self.etype == 'tank':
            pygame.draw.rect(surf, (100, 40, 40), (sx+2, sy+2, s-4, s-4))
        if self.etype == 'berserker':
            # rage aura
            rage = 1.0 - self.hp/self.max_hp
            pygame.draw.rect(surf, (255, int(40*(1-rage)), 0), (sx-1, sy-1, s+2, s+2), 2)

        # eyes
        ex_off = s//4
        pygame.draw.circle(surf, (255,255,255), (sx+ex_off, sy+s//3), 3)
        pygame.draw.circle(surf, (255,255,255), (sx+s-ex_off, sy+s//3), 3)
        pygame.draw.circle(surf, (0,0,0), (sx+ex_off, sy+s//3), 2)
        pygame.draw.circle(surf, (0,0,0), (sx+s-ex_off, sy+s//3), 2)

        # HP bar
        if self.hp < self.max_hp:
            bw = s
            filled = int(bw * self.hp / self.max_hp)
            pygame.draw.rect(surf, (60, 0, 0), (sx, sy-6, bw, 4))
            pygame.draw.rect(surf, (0, 220, 60), (sx, sy-6, filled, 4))