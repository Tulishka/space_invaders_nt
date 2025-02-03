import pygame


def load(name: str, volume: float):
    """Функция загружает саунд-эффект и задает ему громкость
    :param name: имя саунд-эффекта
    :param volume: громкость от 0.0 до 1.0
    :return:
    """
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
    "upgrade_gun": load("sound/upgrade_gun.mp3", 0.3),

    "laser_beam": load("sound/laser_beam.wav", 0.5),
    "alien_dead": load("sound/exp1.wav", 0.3),
    "alien_shot1": load("sound/easy_blaster.wav", 1),
    "alien_shot2": load("sound/blaster2.wav", 1),
    "alien_shot3": load("sound/blaster1.wav", 1),
    "alien_shot7": load("sound/blaster2.wav", 1),
    "alien_warp": load("sound/warp.wav", 0.2),
    "alien_shield_up": load("sound/give_shield.wav", 1),
    "alien_shield_down": load("sound/pop.wav", 1),

    "bonus_alien_lr": load("sound/bonus_alien_lr.wav", 1),
    "bonus_alien_rl": load("sound/bonus_alien_rl.wav", 1),

    "minion_shot": load("sound/blaster1.wav", 0.2),
    "minion_warp": load("sound/minion_warp.wav", 0.5),
    "minion_relocate": load("sound/woosh.wav", 0.3),

    "boss_online": load("sound/boss_online.wav", 0.7),
    "boss_signal": load("sound/boss_signal.wav", 0.7),
    "boss_move": load("sound/boss_move.wav", 0.3),
    "boss_shield_up": load("sound/start2.mp3", 1),
    "boss_shield_down": load("sound/woosh.wav", 1),

    "menu_beep": load("sound/hit2.wav", 1),
    "menu_start": load("sound/start1.mp3", 0.2),
    "menu_show": load("sound/start2.mp3", 0.8),
}


def play_sound(name: str):
    """Воспроизводит подготовленный саунд-эффект
    :param name: имя
    :return None:
    """
    sounds[name].play()


def stop_sound():
    """Останавливает все звуки"""
    pygame.mixer.fadeout(500)
