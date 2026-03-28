import math, pygame

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def vec2_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1])

def vec2_norm(v):
    l = vec2_len(v)
    if l == 0:
        return (0.0, 0.0)
    return (v[0]/l, v[1]/l)

def vec2_dist(a, b):
    return vec2_len((b[0]-a[0], b[1]-a[1]))

def angle_to(src, dst):
    return math.atan2(dst[1]-src[1], dst[0]-src[0])

def rotate_vec(v, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (v[0]*c - v[1]*s, v[0]*s + v[1]*c)

def draw_text(surf, text, x, y, color=(255,255,255), size=16, font=None, anchor="topleft"):
    if font is None:
        font = pygame.font.SysFont("monospace", size, bold=True)
    img = font.render(text, True, color)
    r = img.get_rect()
    setattr(r, anchor, (int(x), int(y)))
    surf.blit(img, r)
    return r

class SpatialHash:
    def __init__(self, cell=64):
        self.cell = cell
        self.grid = {}

    def _key(self, x, y):
        return (int(x)//self.cell, int(y)//self.cell)

    def clear(self):
        self.grid.clear()

    def insert(self, obj, x, y):
        k = self._key(x, y)
        self.grid.setdefault(k, []).append(obj)

    def query(self, x, y, r=0):
        results = []
        cells_r = max(1, int(r/self.cell)+1)
        cx, cy = self._key(x, y)
        for dx in range(-cells_r, cells_r+1):
            for dy in range(-cells_r, cells_r+1):
                results.extend(self.grid.get((cx+dx, cy+dy), []))
        return results

class Timer:
    def __init__(self):
        self._timers = {}

    def set(self, name, duration):
        self._timers[name] = duration

    def update(self, dt):
        for k in list(self._timers):
            self._timers[k] -= dt
            if self._timers[k] <= 0:
                del self._timers[k]

    def active(self, name):
        return name in self._timers

    def remaining(self, name):
        return self._timers.get(name, 0)