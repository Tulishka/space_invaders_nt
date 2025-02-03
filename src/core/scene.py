class Scene:
    """Базовый класс для сцены.
    Сцена нужна, что бы делить приложение на разные экраны.
    Имеет свою логику, отображения и обработку событий.
    Ведёт отсчёт времени.
    """
    keep_alive = False  # Помнить созданную сцену

    def __init__(self, scene_manager, params: dict = None):
        """Конструктор класса.
        :param scene_manager: SceneManager, куда добавляется сцена.
        :param params: Параметры сцены
        """
        self.scene_manager = scene_manager
        self.params = {}
        self.update_params(params)
        self.time = 0

    def update_params(self, params: dict):
        """Метод вызывается при повторном создании сцены.
        :param params:
        :return None:
        """
        if params:
            self.params.update(params)

    def draw(self, screen):
        """Метод вызывается SceneManager-ом, когда нужно нарисовать сцену
        :param screen: куда рисовать
        :return None:
        """
        pass

    def update(self, dt):
        """Метод вызывается, что бы обновить состояние сцены
        :param dt: Время с прошло обновления в сек.
        :return None:
        """
        self.time += dt

    def process_event(self, event) -> bool:
        """Метод вызывается для передачи события в сцену
        Если сцена обработает событие, она должна вернуть False
        :param event: объект события
        :return bool: вернуть True если обработано
        """
        return False

    def on_kill(self):
        """Метод вызывается при уничтожении сцены"""
        pass

    def on_show(self, first_time):
        """Метод вызывается при входе на сцену"""
        pass

    def on_hide(self):
        """Метод вызывается при выходе из сцены"""
        pass
