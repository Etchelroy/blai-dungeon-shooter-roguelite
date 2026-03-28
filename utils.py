import math
import pygame

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, mn, mx):
    return max(mn, min(mx, v))

def vec2_len(x, y):
    return math.sqrt(x*x + y*y)

def vec2_norm(x, y):
    l = vec2_len(x, y)
    if l == 0:
        return 0.0, 0.0
    return x/l, y/l

def vec2_dist(ax, ay, bx, by):
    return math.sqrt((ax-bx)**2 + (ay-by)**2)

def angle_to(ax, ay, bx, by):
    return math.atan2(by - ay, bx - ax)

def move_toward(current, target, step):
    if abs(target - current) <= step:
        return target
    return current + step if target > current else current - step

def rotate_vec(x, y, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x*c - y*s, x*s + y*c

def rect_from_center(cx, cy, w, h):
    return pygame.Rect(cx - w//2, cy - h//2, w, h)

def screen_shake_offset(intensity, timer):
    import random
    if timer <= 0:
        return 0, 0
    ox = random.randint(-int(intensity), int(intensity))
    oy = random.randint(-int(intensity), int(intensity))
    return ox, oy

def draw_text(surf, text, x, y, font, color, center=False, shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        r = s.get_rect()
        if center:
            r.centerx = x
            r.centery = y
        else:
            r.x = x
            r.y = y
        surf.blit(s, (r.x+2, r.y+2))
    img = font.render(text, True, color)
    r = img.get_rect()
    if center:
        r.centerx = x
        r.centery = y
    else:
        r.x = x
        r.y = y
    surf.blit(img, r)
    return r

def hsv_to_rgb(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

def color_lerp(c1, c2, t):
    return (
        int(c1[0] + (c2[0]-c1[0])*t),
        int(c1[1] + (c2[1]-c1[1])*t),
        int(c1[2] + (c2[2]-c1[2])*t),
    )

def pulse(t, speed=2.0, lo=0.5, hi=1.0):
    return lo + (hi-lo) * (0.5 + 0.5*math.sin(t*speed))