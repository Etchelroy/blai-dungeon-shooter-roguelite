import math, random, pygame

def normalize(v):
    x, y = v
    l = math.hypot(x, y)
    if l == 0:
        return (0, 0)
    return (x/l, y/l)

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def angle_to(a, b):
    return math.atan2(b[1]-a[1], b[0]-a[0])

def lerp(a, b, t):
    return a + (b-a)*t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def rand_color_var(base, var=30):
    r = clamp(base[0]+random.randint(-var,var),0,255)
    g = clamp(base[1]+random.randint(-var,var),0,255)
    b = clamp(base[2]+random.randint(-var,var),0,255)
    return (r,g,b)

def draw_bar(surf, x, y, w, h, val, mx, fg, bg=(30,30,30), border=(200,200,200)):
    pygame.draw.rect(surf, bg, (x,y,w,h))
    if mx > 0:
        fw = int(w * clamp(val/mx,0,1))
        if fw > 0:
            pygame.draw.rect(surf, fg, (x,y,fw,h))
    pygame.draw.rect(surf, border, (x,y,w,h), 1)

def rotate_point(px, py, cx, cy, angle):
    s, c = math.sin(angle), math.cos(angle)
    px -= cx; py -= cy
    nx = px*c - py*s
    ny = px*s + py*c
    return nx+cx, ny+cy

def screen_shake_offset(intensity, duration_left):
    if duration_left <= 0:
        return (0,0)
    a = random.uniform(-intensity, intensity)
    b = random.uniform(-intensity, intensity)
    return (a, b)

def circle_rect_overlap(cx, cy, cr, rx, ry, rw, rh):
    nearest_x = clamp(cx, rx, rx+rw)
    nearest_y = clamp(cy, ry, ry+rh)
    return math.hypot(cx-nearest_x, cy-nearest_y) < cr

def point_in_rect(px, py, rx, ry, rw, rh):
    return rx <= px <= rx+rw and ry <= py <= ry+rh