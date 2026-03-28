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
I'll implement the remaining files needed to complete the game. Let me build all the missing systems.

```python
# filename: player.py
import pygame
import math
import time
from constants import *

class Afterimage:
    def __init__(self, pos, image, alpha=150):
        self.pos = list(pos)
        self.image = image.copy()
        self.alpha = alpha
        self.decay = 15

    def update(self):
        self.alpha -= self.decay
        return self.alpha > 0

    def draw(self, surface, camera):
        if self.alpha <= 0:
            return
        img = self.image.copy()
        img.set_alpha(max(0, self.alpha))
        rect = img.get_rect(center=(self.pos[0] - camera.offset_x, self.pos[1] - camera.offset_y))
        surface.blit(img, rect)

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 32
        self.height = 32
        self.speed = PLAYER_SPEED
        self.friction = PLAYER_FRICTION
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.alive = True

        self.dash_cooldown = 0.0
        self.dash_duration = 0.0
        self.dash_vx = 0.0
        self.dash_vy = 0.0
        self.is_dashing = False
        self.i_frames = 0.0
        self.afterimages = []

        self.angle = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0

        self.melee_cooldown = 0.0
        self.melee_active = False
        self.melee_timer = 0.0
        self.melee_angle = 0.0

        self.coins = 0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.kills = 0

        self.weapon_index = 0
        self.secondary_index = 0
        self.ammo = {}
        self.secondary_cooldown = 0.0

        self.image = self._make_image()
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)

        self.invincible_flash = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (80, 160, 255), (0, 0, self.width, self.height))
        pygame.draw.ellipse(surf, (200, 230, 255), (6, 6, self.width-12, self.height-12))
        pygame.draw.circle(surf, (255, 220, 100), (self.width//2 + 10, self.height//2), 5)
        return surf

    def get_rect(self):
        return pygame.Rect(int(self.x - self.width//2), int(self.y - self.height//2), self.width, self.height)

    def take_damage(self, amount):
        if self.i_frames > 0 or self.is_dashing:
            return False
        self.hp -= amount
        self.i_frames = 1.0
        self.invincible_flash = 1.0
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_combo(self):
        self.combo += 1
        self.combo_timer = 3.0
        self.score += 100 * self.combo

    def update(self, dt, keys, mouse_pos, camera, walls):
        mx, my = mouse_pos
        wx = mx + camera.offset_x
        wy = my + camera.offset_y
        dx = wx - self.x
        dy = wy - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.facing_x = dx / dist
            self.facing_y = dy / dist
        self.angle = math.atan2(dy, dx)

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.i_frames > 0:
            self.i_frames -= dt
        if self.invincible_flash > 0:
            self.invincible_flash -= dt * 3

        if self.melee_cooldown > 0:
            self.melee_cooldown -= dt
        if self.melee_active:
            self.melee_timer -= dt
            if self.melee_timer <= 0:
                self.melee_active = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt

        if self.secondary_cooldown > 0:
            self.secondary_cooldown -= dt

        if self.is_dashing:
            self.dash_duration -= dt
            if self.dash_duration <= 0:
                self.is_dashing = False
            else:
                old_x, old_y = self.x, self.y
                self.x += self.dash_vx * dt
                self.y += self.dash_vy * dt
                if self._check_wall_collision(walls):
                    self.x, self.y = old_x, old_y
                    self.is_dashing = False
                if len(self.afterimages) == 0 or (self.x - self.afterimages[-1].pos[0])**2 + (self.y - self.afterimages[-1].pos[1])**2 > 100:
                    self.afterimages.append(Afterimage((self.x, self.y), self.image))
        else:
            ax, ay = 0.0, 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                ay -= self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                ay += self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                ax -= self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                ax += self.speed

            if ax != 0 and ay != 0:
                ax *= 0.7071
                ay *= 0.7071

            self.vx += ax * dt * 10
            self.vy += ay * dt * 10
            self.vx *= (1 - self.friction * dt * 10)
            self.vy *= (1 - self.friction * dt * 10)

            max_speed = self.speed
            spd = math.hypot(self.vx, self.vy)
            if spd > max_speed:
                self.vx = self.vx / spd * max_speed
                self.vy = self.vy / spd * max_speed

            old_x = self.x
            self.x += self.vx * dt
            if self._check_wall_collision(walls):
                self.x = old_x
                self.vx = 0

            old_y = self.y
            self.y += self.vy * dt
            if self._check_wall_collision(walls):
                self.y = old_y
                self.vy = 0

        self.afterimages = [a for a in self.afterimages if a.update()]
        self.rect = self.get_rect()

    def _check_wall_collision(self, walls):
        r = self.get_rect()
        for w in walls:
            if r.colliderect(w):
                return True
        return False

    def try_dash(self):
        if self.dash_cooldown <= 0 and not self.is_dashing:
            spd = math.hypot(self.vx, self.vy)
            if spd < 10:
                dx, dy = self.facing_x, self.facing_y
            else:
                dx, dy = self.vx / spd, self.vy / spd
            self.dash_vx = dx * DASH_SPEED
            self.dash_vy = dy * DASH_SPEED
            self.dash_duration = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            self.is_dashing = True
            self.i_frames = DASH_DURATION + 0.1
            return True
        return False

    def try_melee(self):
        if self.melee_cooldown <= 0:
            self.melee_cooldown = MELEE_COOLDOWN
            self.melee_active = True
            self.melee_timer = MELEE_DURATION
            self.melee_angle = self.angle
            return True
        return False

    def get_melee_rect(self):
        if not self.melee_active:
            return None
        reach = MELEE_RANGE
        cx = self.x + math.cos(self.melee_angle) * reach * 0.5
        cy = self.y + math.sin(self.melee_angle) * reach * 0.5
        return pygame.Rect(int(cx - reach//2), int(cy - reach//2), reach, reach)

    def draw(self, surface, camera):
        for a in self.afterimages:
            a.draw(surface, camera)

        sx = int(self.x - camera.offset_x)
        sy = int(self.y - camera.offset_y)

        if self.invincible_flash > 0 and int(self.invincible_flash * 10) % 2 == 0:
            pass
        else:
            rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
            rect = rotated.get_rect(center=(sx, sy))
            surface.blit(rotated, rect)

        if self.melee_active:
            self._draw_melee(surface, camera)

    def _draw_melee(self, surface, camera):
        sx = int(self.x - camera.offset_x)
        sy = int(self.y - camera.offset_y)
        angle = self.melee_angle
        arc_surf = pygame.Surface((MELEE_RANGE*2, MELEE_RANGE*2), pygame.SRCALPHA)
        spread = math.pi / 3
        start_a = angle - spread
        points = [(MELEE_RANGE, MELEE_RANGE)]
        steps = 12
        for i in range(steps+1):
            a = start_a + spread * 2 * i / steps
            points.append((MELEE_RANGE + math.cos(a)*MELEE_RANGE, MELEE_RANGE + math.sin(a)*MELEE_RANGE))
        if len(points) > 2:
            pygame.draw.polygon(arc_surf, (255, 200, 50, 80), points)
            pygame.draw.polygon(arc_surf, (255, 220, 100, 160), points, 2)
        surface.blit(arc_surf, (sx - MELEE_RANGE, sy - MELEE_RANGE))