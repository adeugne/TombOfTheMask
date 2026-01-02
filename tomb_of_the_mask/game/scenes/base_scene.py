class BaseScene:
    def __init__(self):
        self.next_scene = None

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
