class Scene:
    def __init__(self, scene_manager, params=None):
        self.scene_manager = scene_manager
        self.params = params
        self.time = 0

    def draw(self, screen):
        pass

    def update(self, dt):
        self.time += dt

    def process_event(self, event) -> bool:
        return False
