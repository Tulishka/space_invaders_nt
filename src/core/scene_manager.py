from src.core.scene import Scene


class SceneManager:
    """Класс для работы со сценами: создание, переключения, обновления.

    В классе одна текущая (активная) сцена - она получает обновления, события
    и используется для отрисовки на экран.
    Класс работает как стек. При добавлении новой сцены она добавляется на вершину стека
    и становится активной.
    """

    def __init__(self):
        self.scenes_classes = {}
        self.created_scenes = {}  # кеш созданных сцен
        self.scenes_stack = []

    def current_scene(self) -> Scene:
        """Метод возвращает текущую сцену

        :return Scene:
        """
        if not self.scenes_stack:
            raise Exception("Нет сцен!")
        return self.scenes_stack[-1]

    def pop_scene(self, call_prev=True) -> Scene:
        """Удаляет сцену с вершины стека, возвращаясь к предыдущей.

        :param call_prev: Уведомить новую сцену о том, что она стала активна
        :return Scene:
        """
        current_scene = self.scenes_stack.pop()
        current_scene.on_hide()
        if not current_scene.keep_alive:
            self.kill_scene(current_scene)
        if call_prev and self.scenes_stack:
            self.current_scene().on_show(False)
        return current_scene

    def push_scene(self, scene_name: str, params: dict = None, call_prev=True):
        """Метод добавляет новую сцену на вершину стека

        :param scene_name: Имя сцены.
        :param params: Параметры для сцены.
        :param call_prev: Уведомить предыдущую сцену, что она стала неактивна.
        :return:
        """
        if self.scenes_stack and call_prev:
            self.current_scene().on_hide()
        if scene_name in self.created_scenes:
            new_scene = self.created_scenes[scene_name]
            new_scene.update_params(params)
            new_scene.on_show(False)
        else:
            new_scene = self.scenes_classes[scene_name](self, params)
            self.created_scenes[scene_name] = new_scene
            new_scene.on_show(True)
        self.scenes_stack.append(new_scene)

    def change_scene(self, scene_name: str, params: dict = None):
        """Сменить сцену на вершине стека

        :param scene_name: имя новой сцены
        :param params: параметры для сцены
        :return:
        """
        self.pop_scene(False)
        self.push_scene(scene_name, params, False)

    def add_scene_class(self, name, clas):
        """Добавляет класс в менеджера сцен"""
        self.scenes_classes[name] = clas

    def kill_scene(self, scene: str | Scene):
        """Уничтожает сцену.

        :param scene: Имя или объект сцены
        :return:
        """
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
        """Обновление текущей сцены

        :param dt: время с прошлого раза в сек.
        :return None:
        """
        self.current_scene().update(dt)

    def draw(self, screen):
        """Вызывается для отрисовки текущей сцены

        :param screen: поверхность куда рисовать
        :return None:
        """
        self.current_scene().draw(screen)

    def process_event(self, event):
        """Передает в текущую сцену событие для обработки

        :param event: объект событие
        :return bool: возвращает True если событие обработано
        """
        return self.current_scene().process_event(event)
