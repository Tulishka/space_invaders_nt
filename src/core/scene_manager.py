from src.core.scene import Scene


class SceneManager:

    def __init__(self):
        self.scenes_classes = {}
        self.created_scenes = {}
        self.scenes_stack = []

    def current_scene(self) -> Scene:
        if not self.scenes_stack:
            raise Exception("Нет сцен!")
        return self.scenes_stack[-1]

    def pop_scene(self, call_prev=True):
        current_scene = self.scenes_stack.pop()
        current_scene.on_hide()
        if not current_scene.keep_alive:
            self.kill_scene(current_scene)
        if call_prev and self.scenes_stack:
            self.current_scene().on_show(False)
        return current_scene

    def push_scene(self, scene_name, params=None, call_prev=True):
        if self.scenes_stack and call_prev:
            self.current_scene().on_hide()
        if scene_name in self.created_scenes:
            new_scene = self.created_scenes[scene_name]
            new_scene.update_params(params)
            new_scene.on_show(True)
        else:
            new_scene = self.scenes_classes[scene_name](self, params)
            self.created_scenes[scene_name] = new_scene
            new_scene.on_show(False)
        self.scenes_stack.append(new_scene)

    def change_scene(self, scene_name, params=None):
        self.pop_scene(False)
        self.push_scene(scene_name, params, False)

    def add_scene_class(self, name, clas):
        self.scenes_classes[name] = clas

    def kill_scene(self, scene: str | Scene):
        if isinstance(scene, str):
            scene = self.created_scenes.pop(scene, None)
        else:
            name = [name for name, val in self.created_scenes.items() if val is scene]
            if name:
                self.created_scenes.pop(name[0])
        if scene:
            scene.on_kill()
        if scene in self.scenes_stack:
            self.scenes_stack.remove(scene)

    def update(self, dt):
        self.current_scene().update(dt)

    def draw(self, screen):
        self.current_scene().draw(screen)

    def process_event(self, event):
        return self.current_scene().process_event(event)
