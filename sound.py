import pygame


def load(name, volume):
    sound = pygame.mixer.Sound(name)
    sound.set_volume(volume)
    return sound


pygame.mixer.init()

sounds = {
    "player_shot1": load("sound/laser1.wav", 0.8),
    "player_shot2": load("sound/laser2.wav", 0.8),

    "player_hit": load("sound/exp2.wav", 1),

    "menu_beep": load("sound/hit2.wav", 1),
    "menu_start": load("sound/start1.mp3", 0.2),

    "alien_dead": load("sound/exp1.wav", 0.3),

}


def play_sound(name):
    sounds[name].play()
