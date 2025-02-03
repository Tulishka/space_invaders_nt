from random import random


class Cooldown:

    def __init__(self, parent, interval=99999, random_delta: float = 0, started=False):
        """
        :param parent: Объект - содержит свойство time float в секундах
        :param interval: время "остывания" в сек
        """
        self.random_delta = random_delta
        self._start_time = parent.time - 99999 * (not started)
        self.interval = interval
        self.parent = parent
        if not hasattr(self.parent, "time"):
            raise TypeError("parent должен содержать свойство 'time'")

    def reset(self):
        """ Сброс процесса остывания """
        self._start_time = self.parent.time - self.interval

    def __call__(self, *args, **kwargs):
        return self.is_ready()

    def is_ready(self):
        """ Остывание завершено? """
        return self._start_time + self.interval < self.parent.time

    def get_progress(self):
        """ Прогресс остывание - число от 0 до 1 """
        if self.interval == 0:
            return 1
        a = (self.parent.time - self._start_time) / self.interval
        return 1 if a > 1 else 0 if a < 0 else a

    def start(self, shift=0):
        """Вызвать когда нужно начать отсчет времени "остывания" """
        self._start_time = self.parent.time + shift
        if self.random_delta > 0:
            self._start_time += self.random_delta * random() - self.random_delta / 2

    def __bool__(self):
        return self.is_ready()
