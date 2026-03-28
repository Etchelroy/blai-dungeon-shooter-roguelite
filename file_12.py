import math, pygame, random
from src.utils import vec2_norm

class Ability:
    def __init__(self, name, cooldown, duration=0):
        self.name=name; self.cooldown_max=cooldown
        self.cooldown=0.0; self.duration=duration
        self.active=False;