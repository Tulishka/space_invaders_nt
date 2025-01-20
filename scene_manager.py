from scene import Scene


class SceneManager:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1150, 750

    def __init__(self):
        self.scenes = {}
        self.empty_scene = Scene(self)
        self.current_scene = self.empty_scene

    def set_scene(self, scene_name, params=None):
        self.current_scene = self.scenes[scene_name](self, params)

    def add_scene(self, name, clas):
        self.scenes[name] = clas

    def update(self, dt):
        self.current_scene.update(dt)

    def draw(self, screen):
        self.current_scene.draw(screen)

    def process_event(self, event):
        return self.current_scene.process_event(event)
