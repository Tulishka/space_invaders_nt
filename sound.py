import pygame


def load(name, volume):
    sound = pygame.mixer.Sound(name)
    sound.set_volume(volume)
    return sound


pygame.mixer.init()

sounds = {
    "player_dead": load("sound/exp2.wav", 0.3),
    "player_stasis": load("sound/exp2.wav", 0.3),
    "player_shot1": load("sound/laser1.wav", 0.8),
    "player_shot2": load("sound/laser2.wav", 0.8),
    "player_hit": load("sound/exp2.wav", 1),

    "alien_dead": load("sound/exp1.wav", 0.3),
    "alien_shot1": load("sound/easy_blaster.wav", 1),
    "alien_shot2": load("sound/blaster2.wav", 1),
    "alien_shot3": load("sound/blaster1.wav", 1),

    "bonus_alien_lr": load("sound/bonus_alien_lr.wav", 1),
    "bonus_alien_rl": load("sound/bonus_alien_rl.wav", 1),

    "menu_beep": load("sound/hit2.wav", 1),
    "menu_start": load("sound/start1.mp3", 0.2),

}


def play_sound(name):
    sounds[name].play()
