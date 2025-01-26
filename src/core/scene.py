class Scene:
    def __init__(self, scene_manager, params=None):
        self.scene_manager = scene_manager
        self.params = {}
        self.update_params(params)
        self.time = 0

    def update_params(self, params):
        if params:
            self.params.update(params)

    def draw(self, screen):
        pass

    def update(self, dt):
        self.time += dt

    def process_event(self, event) -> bool:
        return False

    def on_kill(self):
        pass

    def on_show(self, first_time):
        pass

    def on_hide(self):
        pass
