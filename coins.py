import pygame
import math
import random

class Coin:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.value = value
        self.alive = True
        self.bob_timer = random.uniform(0, math.pi * 2)
        self.magnet_speed = 0
        self.vel_x = random.uniform(-60, 60)
        self.vel_y = random.uniform(-100, -40)
        self.on_ground = False
        self.color = (255, 215, 0) if value == 1 else (200, 200, 255)
        self.radius = 8 if value == 1 else 10
        self.collect_radius = 60

    def update(self, dt, player_rect):
        self.bob_timer += dt * 3
        if not self.on_ground:
            self.vel_y += 300 * dt
            self.x += self.vel_x * dt
            self.y += self.vel_y * dt
            if self.vel_y > 0 and self.y > self.y:
                self.on_ground = True
                self.vel_x = 0
                self.vel_y = 0

        px, py = player_rect.centerx, player_rect.centery
        dist = math.hypot(px - self.x, py - self.y)
        if dist < self.collect_radius:
            speed = 300 + (self.collect_radius - dist) * 5
            if dist > 1:
                self.x += (px - self.x) / dist * speed * dt
                self.y += (py - self.y) / dist * speed * dt
        if dist < 20:
            self.alive = False
            return self.value
        return 0

    def draw(self, surface, camera):
        if not self.alive:
            return
        from camera import Camera
        sx, sy = camera.world_to_screen(self.x, self.y)
        bob = math.sin(self.bob_timer) * 3
        pygame.draw.circle(surface, self.color, (int(sx), int(sy + bob)), self.radius)
        pygame.draw.circle(surface, (255, 255, 200), (int(sx) - 2, int(sy + bob) - 2), self.radius // 3)
        pygame.draw.circle(surface, (180, 140, 0), (int(sx), int(sy + bob)), self.radius, 2)

class CoinManager:
    def __init__(self):
        self.coins = []
        self.total = 0

    def spawn(self, x, y, count=1, value=1):
        for _ in range(count):
            ox = x + random.uniform(-20, 20)
            oy = y + random.uniform(-20, 20)
            self.coins.append(Coin(ox, oy, value))

    def update(self, dt, player_rect):
        collected = 0
        for c in self.coins:
            if c.alive:
                v = c.update(dt, player_rect)
                collected += v
        self.coins = [c for c in self.coins if c.alive]
        self.total += collected
        return collected

    def draw(self, surface, camera):
        for c in self.coins:
            c.draw(surface, camera)