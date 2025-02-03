class ItemsMenu:
    """Базовый класс для меню из элементов.
    Содержит методы для уведомления меню о том,
    что элементы выбраны или активированы
    """

    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def item_activated(self, item):
        pass

    def item_selected(self, item):
        pass
