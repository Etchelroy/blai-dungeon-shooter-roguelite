import pygame

class Animation:
    def __init__(self, frames, frame_duration, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.elapsed = 0.0
        self.current_frame = 0
        self.done = False

    def update(self, dt):
        if self.done:
            return
        self.elapsed += dt
        if self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.done = True

    def get_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.elapsed = 0.0
        self.current_frame = 0
        self.done = False

class AnimationController:
    def __init__(self):
        self.animations = {}
        self.current = None
        self.current_name = None

    def add(self, name, anim):
        self.animations[name] = anim

    def play(self, name, force=False):
        if self.current_name == name and not force:
            return
        if name in self.animations:
            self.current_name = name
            self.current = self.animations[name]
            self.current.reset()

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def get_frame(self):
        if self.current:
            return self.current.get_frame()
        return None