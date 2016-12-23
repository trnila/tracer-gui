class Frame:
    def __init__(self, content, backtrace=[]):
        self.content = content
        self.backtrace = backtrace


class Backtrace:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame):
        self.frames.append(frame)
