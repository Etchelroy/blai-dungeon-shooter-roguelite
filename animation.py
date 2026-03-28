class AnimationFrame:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

class Animation:
    def __init__(self, frames, loop=True):
        self.frames = frames
        self.loop = loop
        self.current = 0
        self.timer = 0.0
        self.done = False
        self.frame_index = 0

    def update(self, dt):
        if self.done:
            return
        self.timer += dt
        if self.frames and self.timer >= self.frames[self.current].duration:
            self.timer -= self.frames[self.current].duration
            self.current += 1
            if self.current >= len(self.frames):
                if self.loop:
                    self.current = 0
                else:
                    self.current = len(self.frames)-1
                    self.done = True
        self.frame_index = self.current

    def get_frame_name(self):
        if self.frames:
            return self.frames[self.current].name
        return 'idle'

    def reset(self):
        self.current = 0
        self.timer = 0.0
        self.done = False
        self.frame_index = 0

class AnimationController:
    def __init__(self):
        self.animations = {}
        self.current_anim = None
        self.current_name = ''
        self.frame_counter = 0.0

    def add(self, name, frames_list, loop=True):
        frames = [AnimationFrame(n, d) for n, d in frames_list]
        self.animations[name] = Animation(frames, loop)

    def play(self, name, force=False):
        if name not in self.animations:
            return
        if self.current_name == name and not force:
            return
        self.current_name = name
        self.current_anim = self.animations[name]
        self.current_anim.reset()

    def update(self, dt):
        self.frame_counter += dt * 60
        if self.current_anim:
            self.current_anim.update(dt)

    def get_frame(self):
        if self.current_anim:
            return self.current_anim.frame_index
        return 0

    def is_done(self):
        if self.current_anim:
            return self.current_anim.done
        return True