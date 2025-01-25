import pygame

music = {
    "next_level": ("music/next_level.mp3", 0.5),
    "boss": ("music/boss.mp3", 0.25),
    "gameover": ("music/gameover.mp3", 1),
    "menu": ("music/menu1.mp3", 0.5),
    "victory": ("music/victory.mp3", 0.5),
}


def play(name, loops=0, start=0):
    file, volume = music[name]
    pygame.mixer_music.load(file)
    pygame.mixer_music.set_volume(volume)
    pygame.mixer_music.play(loops, start)


def stop(stop_time=500):
    pygame.mixer_music.fadeout(stop_time)
