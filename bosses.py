import pygame
import math
import random
from constants import *

class BossBase:
    def __init__(self, x, y, name, hp, color, size=48):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.size = size
        self.alive = True
        self.phase = 1
        self.phase_transitions = [0.66, 0.33]
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 60
        self.damage_flash = 0.0
        self.attack_timer = 0.0
        self.stun_timer = 0.0
        self.drop_coins = 20
        self.score_value = 5000
        self.death_sequence = False
        self.death_timer = 3.0
        self.vulnerable = True
        self.vulnerability_timer = 0.0
        self.invuln_timer = 0.0
        self.image = self._make_image()
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.angle = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surf, (255,255,255), (self.size, self.size), self.size, 3)
        return surf

    def get_rect(self):
        return pygame.Rect(int(self.x-self.size), int(self.y-self.size), self.size*2, self.size*2)

    def take_damage(self, amount, kx=0, ky=0):
        if not self.vulnerable or self.invuln_timer > 0:
            return
        self.hp -= amount
        self.damage_flash = 0.2
        self.knockback_x = kx * 100
        self.knockback_y = ky * 100
        if self.hp <= 0:
            self.hp = 0
            if not self.death_sequence:
                self.death_sequence = True
        else:
            hp_ratio = self.hp / self.max_hp
            if self.phase == 1 and hp_ratio <= self.phase_transitions[0]:
                self.phase = 2
                self.on_phase_change(2)
            elif self.phase == 2 and hp_ratio <= self.phase_transitions[1]:
                self.phase = 3
                self.on_phase_change(3)

    def on_phase_change(self, phase):
        self.invuln_timer = 2.0
        self.speed += 20

    def update(self, dt, player, walls, projectiles_out, particles_out):
        if self.death_sequence:
            self.death_timer -= dt
            self._death_effect(dt, particles_out)
            return self.death_timer <= 0

        if self.stun_timer > 0:
            self.stun_timer -= dt
        if self.damage_flash > 0:
            self.damage_flash -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            self.vulnerable = False
        else:
            self.vulnerable = True
        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.knockback_x *= (1 - 5*dt)
        self.knockback_y *= (1 - 5*dt)
        self.x += self.knockback_x * dt
        self.y += self.knockback_y * dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx,dy)
        if dist > 0:
            self.angle = math.atan2(dy,dx)

        self.phase_update(dt, player, walls, projectiles_out, particles_out)
        return False

    def phase_update(self, dt, player, walls, projectiles_out, particles_out):
        pass

    def _death_effect(self, dt, particles_out):
        if random.random() < 0.3:
            from particles import Particle
            px = self.x + random.uniform(-self.size, self.size)
            py = self.y + random.uniform(-self.size, self.size)
            particles_out.append(Particle(px, py,
                random.uniform(-100,100), random.uniform(-100,100),
                random.choice([(255,100,0),(255,200,50),(220,80,0)]),
                random.uniform(0.3,0.8), random.uniform(3,8)))

    def _move_toward(self, tx, ty, dt, walls):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            nx, ny = dx/dist, dy/dist
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt

    def _shoot_radial(self, count, speed, damage, color, projectiles_out):
        from projectiles import EnemyProjectile
        for i in range(count):
            a = i * math.pi * 2 / count
            projectiles_out.append(EnemyProjectile(self.x, self.y, math.cos(a), math.sin(a),
                speed=speed, damage=damage, color=color))

    def _shoot_at_player(self, player, speed, damage, color, projectiles_out, spread=0):
        from projectiles import EnemyProjectile
        dx = player.x - self.x
        dy = player.y - self.y
        d = math.hypot(dx,dy)
        if d == 0: return
        base_a = math.atan2(dy,dx)
        a = base_a + random.uniform(-spread, spread)
        projectiles_out.append(EnemyProjectile(self.x, self.y, math.cos(a), math.sin(a),
            speed=speed, damage=damage, color=color))

    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x)
        sy = int(self.y - camera.offset_y)
        if self.damage_flash > 0 and int(self.damage_flash*20)%2==0:
            img = self.image.copy()
            img.fill((255,80,80,0), special_flags=pygame.BLEND_ADD)
            surface.blit(img, (sx-self.size, sy-self.size))
        else:
            surface.blit(self.image, (sx-self.size, sy-self.size))
        if not self.vulnerable:
            pygame.draw.circle(surface, (200,200,200,100), (sx,sy), self.size+6, 3)

class BossVoidBringer(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Void Bringer", hp=1500, color=(80,0,120), size=48)
        self.orbit_angle = 0.0
        self.orbit_speed = 1.5
        self.wave_timer = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80,0,120), (self.size,self.size), self.size)
        for i in range(6):
            a = i * math.pi/3
            x1 = self.size + math.cos(a)*20
            y1 = self.size + math.sin(a)*20
            x2 = self.size + math.cos(a)*self.size
            y2 = self.size + math.sin(a)*self.size
            pygame.draw.line(surf, (200,100,255), (int(x1),int(y1)), (int(x2),int(y2)), 3)
        pygame.draw.circle(surf, (200,100,255), (self.size,self.size), 15)
        pygame.draw.circle(surf, (255,255,255), (self.size,self.size), self.size, 2)
        return surf

    def on_phase_change(self, phase):
        super().on_phase_change(phase)
        self.orbit_speed += 0.8

    def phase_update(self, dt, player, walls, projectiles_out, particles_out):
        self.orbit_angle += self.orbit_speed * dt
        if self.phase == 1:
            self._phase1(dt, player, walls, projectiles_out)
        elif self.phase == 2:
            self._phase2(dt, player, walls, projectiles_out)
        else:
            self._phase3(dt, player, walls, projectiles_out, particles_out)

    def _phase1(self, dt, player, walls, projectiles_out):
        self._move_toward(player.x, player.y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 2.0
            self._shoot_radial(8, 180, 12, (180,80,255), projectiles_out)

    def _phase2(self, dt, player, walls, projectiles_out):
        # Orbit player
        target_x = player.x + math.cos(self.orbit_angle) * 200
        target_y = player.y + math.sin(self.orbit_angle) * 200
        self._move_toward(target_x, target_y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 1.5
            self._shoot_radial(12, 200, 15, (220,80,255), projectiles_out)
            self._shoot_at_player(player, 300, 18, (255,200,255), projectiles_out)

    def _phase3(self, dt, player, walls, projectiles_out, particles_out):
        self.wave_timer -= dt
        target_x = player.x + math.cos(self.orbit_angle) * 150
        target_y = player.y + math.sin(self.orbit_angle) * 150
        self._move_toward(target_x, target_y, dt, walls)
        if self.attack_timer <= 0:
            self.attack_timer = 1.0
            self._shoot_radial(16, 220, 18, (255,100,255), projectiles_out)
        if self.wave_timer <= 0:
            self.wave_timer = 3.0
            for i in range(24):
                a = i * math.pi*2/24
                self._shoot_at_player(player, 250+random.uniform(-50,50), 20,
                                     (200,50,255), projectiles_out, spread=0.1)

class BossInferno(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Inferno", hp=1800, color=(220,80,20), size=52)
        self.flame_wall_timer = 0.0
        self.dash_timer = 0.0
        self.dashing = False
        self.dash_vx = 0
        self.dash_vy = 0
        self.dash_dur = 0.0

    def _make_image(self):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (220,80,20), (0,0,self.size*2, self.size*2))
        pygame.draw.ellipse(surf, (255,160,50), (8,8, self.size*2-16, self.size*2-16))
        pygame.draw.ellipse(surf, (255,220,100), (self.size-10, self.size-10, 20,20))
        for i in range(8):
            a = i * math.pi/4
            x1 = self.size + math.cos(a)*(self.size-8)
            y1 = self.size + math.sin(a)*(self.size-8)
            x2 = self.size + math.cos(a)*self.size + random.uniform(-4,4)
            y2 = self.size + math.sin(a)*self.size + random.uniform(-4