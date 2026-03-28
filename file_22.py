import pygame
import math
import random
from settings import *

class Assets:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._built = False
        return cls._instance

    def __init__(self):
        if self._built:
            return
        self._built = True
        self.surfaces = {}
        self._build_all()

    def _build_all(self):
        self._build_player()
        self._build_enemies()
        self._build_tiles()
        self._build_ui()
        self._build_bullets()
        self._build_icons()

    def _pixel_art(self, pixels, scale=3):
        h = len(pixels)
        w = len(pixels[0])
        surf = pygame.Surface((w*scale, h*scale), pygame.SRCALPHA)
        for r, row in enumerate(pixels):
            for c, col in enumerate(row):
                if col:
                    pygame.draw.rect(surf, col, (c*scale, r*scale, scale, scale))
        return surf

    def _build_player(self):
        B = (60,80,200)
        W = (220,220,220)
        S = (180,140,100)
        _ = None
        pixels = [
            [_,_,B,B,B,B,_,_],
            [_,B,B,B,B,B,B,_],
            [B,B,W,B,B,W,B,B],
            [B,B,B,B,B,B,B,B],
            [_,B,B,B,B,B,B,_],
            [_,S,B,_,_,B,S,_],
            [_,S,S,_,_,S,S,_],
            [_,S,_,_,_,_,S,_],
        ]
        self.surfaces['player'] = self._pixel_art(pixels, 3)

    def _build_enemies(self):
        configs = {
            'grunt':    [(255,80,80), self._enemy_pixels('grunt')],
            'runner':   [(255,140,40), self._enemy_pixels('runner')],
            'tank':     [(120,40,200), self._enemy_pixels('tank')],
            'shooter':  [(60,200,60), self._enemy_pixels('shooter')],
            'ghost':    [(180,180,255), self._enemy_pixels('ghost')],
            'bomber':   [(255,60,60), self._enemy_pixels('bomber')],
            'shielder': [(200,200,60), self._enemy_pixels('shielder')],
            'healer':   [(60,220,180), self._enemy_pixels('healer')],
            'splitter': [(200,100,60), self._enemy_pixels('splitter')],
            'charger':  [(220,60,220), self._enemy_pixels('charger')],
        }
        for name, (color, px) in configs.items():
            self.surfaces[f'enemy_{name}'] = self._pixel_art(px, 3)

    def _enemy_pixels(self, name):
        R = (220,60,60)
        G = (60,200,60)
        B = (60,60,220)
        P = (180,60,220)
        Y = (220,200,60)
        C = (60,200,200)
        W = (220,220,220)
        _ = None
        if name == 'grunt':
            return [
                [_,R,R,R,R,_],
                [R,R,W,R,W,R],
                [R,R,R,R,R,R],
                [_,R,R,R,R,_],
                [R,_,R,R,_,R],
                [R,_,_,_,_,R],
            ]
        elif name == 'runner':
            return [
                [_,Y,Y,Y,_],
                [Y,Y,W,Y,Y],
                [_,Y,Y,Y,_],
                [Y,Y,Y,Y,Y],
                [Y,_,_,_,Y],
            ]
        elif name == 'tank':
            T = (80,40,160)
            return [
                [T,T,T,T,T,T,T,T],
                [T,T,W,T,T,W,T,T],
                [T,T,T,T,T,T,T,T],
                [T,T,T,T,T,T,T,T],
                [T,T,T,T,T,T,T,T],
                [T,_,T,T,T,T,_,T],
                [T,_,_,_,_,_,_,T],
            ]
        elif name == 'shooter':
            return [
                [_,G,G,G,_],
                [G,G,W,G,G],
                [G,G,G,G,G],
                [G,G,G,G,G],
                [G,_,G,_,G],
            ]
        elif name == 'ghost':
            GH = (140,140,220)
            return [
                [_,_,GH,GH,GH,_,_],
                [_,GH,GH,W,GH,GH,_],
                [GH,GH,GH,GH,GH,GH,GH],
                [GH,GH,GH,GH,GH,GH,GH],
                [GH,_,GH,_,GH,_,GH],
            ]
        elif name == 'bomber':
            return [
                [_,R,R,R,_],
                [R,R,W,R,R],
                [R,R,R,R,R],
                [R,R,R,R,R],
                [_,R,R,R,_],
            ]
        elif name == 'shielder':
            SH = (180,180,60)
            return [
                [_,SH,SH,SH,_],
                [SH,SH,W,SH,SH],
                [SH,SH,SH,SH,SH],
                [SH,SH,SH,SH,SH],
                [SH,_,SH,_,SH],
            ]
        elif name == 'healer':
            return [
                [_,C,C,C,_],
                [C,C,W,C,C],
                [C,C,C,C,C],
                [_,C,C,C,_],
                [C,_,C,_,C],
            ]
        elif name == 'splitter':
            SP = (180,100,40)
            return [
                [SP,SP,SP,SP,SP],
                [SP,W,SP,W,SP],
                [SP,SP,SP,SP,SP],
                [_,SP,SP,SP,_],
            ]
        else:  # charger
            CH = (200,40,200)
            return [
                [_,CH,CH,CH,_],
                [CH,CH,W,CH,CH],
                [CH,CH,CH,CH,CH],
                [CH,CH,CH,CH,CH],
                [CH,_,_,_,CH],
                [CH,_,_,_,CH],
            ]

    def _build_tiles(self):
        tile_defs = {
            'floor': (60,55,70),
            'wall': (40,35,55),
            'lava': (200,80,20),
            'ice': (140,180,255),
            'spikes': (160,160,160),
            'poison': (60,180,60),
            'crate': (140,100,50),
            'floor2': (70,60,80),
            'floor3': (55,50,65),
        }
        for name, color in tile_defs.items():
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill(color)
            r = random.Random(hash(name))
            for _ in range(8):
                nx = r.randint(0, TILE_SIZE-4)
                ny = r.randint(0, TILE_SIZE-4)
                nw = r.randint(2, 6)
                nh = r.randint(2, 4)
                nc = tuple(clamp(c + r.randint(-20,20), 0, 255) for c in color)
                pygame.draw.rect(s, nc, (nx, ny, nw, nh))
            self.surfaces[f'tile_{name}'] = s

    def _build_ui(self):
        pass

    def _build_bullets(self):
        for name, color, r in [('bullet', (255,220,60), 4), ('big_bullet', (255,100,60), 7),
                                 ('pellet', (255,200,80), 3), ('plasma', (100,200,255), 5)]:
            s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (r+1, r+1), r)
            self.surfaces[name] = s

    def _build_icons(self):
        for name, color in [('dash_icon', (100,200,255)), ('melee_icon', (255,140,60)),
                              ('hp_icon', (255,80,80)), ('ammo_icon', (255,220,60))]:
            s = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (12,12), 10)
            self.surfaces[name] = s

    def get(self, name):
        return self.surfaces.get(name)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))