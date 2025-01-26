from src.core.scene import Scene


class SceneManager:

    def __init__(self):
        self.scenes = {}
        self.active_scenes = {}
        self.empty_scene = Scene(self)
        self.current_scene = self.empty_scene

    def set_scene(self, scene_name, params=None):
        if self.current_scene != self.empty_scene and self.current_scene != self.active_scenes.get(scene_name):
            self.current_scene.on_hide()
        if scene_name in self.active_scenes:
            self.current_scene = self.active_scenes[scene_name]
            self.current_scene.update_params(params)
            self.current_scene.on_show(True)
        else:
            self.current_scene = self.scenes[scene_name](self, params)
            self.active_scenes[scene_name] = self.current_scene
            self.current_scene.on_show(False)

    def add_scene(self, name, clas):
        self.scenes[name] = clas

    def kill_scene(self, scene_name):
        scene = self.active_scenes.pop(scene_name, None)
        if scene:
            scene.on_kill()
        if self.current_scene == scene:
            self.current_scene = self.empty_scene

    def update(self, dt):
        self.current_scene.update(dt)

    def draw(self, screen):
        self.current_scene.draw(screen)

    def process_event(self, event):
        return self.current_scene.process_event(event)
