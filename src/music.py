import pygame

# словарь композиций содержит файл с музыкой и громкость для воспроизведения
music = {
    "next_level": ("music/next_level.mp3", 0.5),
    "boss": ("music/boss.mp3", 0.25),
    "gameover": ("music/gameover.mp3", 1),
    "menu": ("music/menu1.mp3", 0.5),
    "victory": ("music/victory.mp3", 0.3),
    "credits": ("music/credits.mp3", 0.7),
    "ost_rus": ("music/ost_track_rus.mp3", 1),
    "ost_eng": ("music/ost_track_eng.mp3", 1),
}


def play(name: str, loops: int = 0, start=0):
    """Воспроизводит нужную музыку
    :param name: имя композиций
    :param loops: число циклов повторения
    :param start: время начала композиции
    :return:
    """
    file, volume = music[name]
    pygame.mixer_music.load(file)
    pygame.mixer_music.set_volume(volume)
    pygame.mixer_music.play(loops, start)


def stop(stop_time=500):
    """Останавливает воспроизведение музыки
    :param stop_time: время затухания в мсек.
    :return:
    """
    pygame.mixer_music.fadeout(stop_time)
