import pygame, math

class LightSource:
    def __init__(self, x, y, radius, color=(255,220,150), intensity=1.0, flicker=False):
        self.x=x; self.y=y; self.radius=radius
        self.color=color; self.intensity=intensity
        self.flicker=flicker
        self._flicker_t=0.0

    def update(self, dt):
        if self.flicker:
            import random
            self._flicker_t += dt*10
            self.intensity = 0.8 + 0.2*math.sin(self._flicker_t) + random.uniform(-0.05,0.05)

class LightingSystem:
    def __init__(self, vw, vh):
        self.vw=vw; self.vh=vh
        self.surf = pygame.Surface((vw,vh), pygame.SRCALPHA)
        self.sources = []
        self.ambient = 40

    def clear(self):
        self.sources.clear()

    def add(self, light):
        self.sources.append(light)

    def update(self, dt):
        for l in self.sources:
            l.update(dt)

    def render(self, cam_x, cam_y):
        self.surf.fill((0,0,0,255-self.ambient))
        for src in self.sources:
            sx = int(src.x - cam_x)
            sy = int(src.y - cam_y)
            r = int(src.radius * src.intensity)
            if sx+r < 0 or sx-r > self.vw or sy+r < 0 or sy-r > self.vh:
                continue
            light_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            for step in range(5, r, max(1,r//8)):
                t = 1 - step/r
                alpha = int(220 * t * src.intensity)
                cr = min(255, int(src.color[0]*t))
                cg = min(255, int(src.color[1]*t))
                cb = min(255, int(src.color[2]*t))
                pygame.draw.circle(light_surf, (cr,cg,cb,alpha), (r,r), step)
            self.surf.blit(light_surf, (sx-r, sy-r), special_flags=pygame.BLENDMODE_NONE)
            pygame.draw.circle(self.surf, (0,0,0,0), (sx,sy), max(1,r//4))
        return self.surf