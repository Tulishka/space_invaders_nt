class LevelSettings:
    def __init__(self,
                 alien_in_line: int,
                 alien_types: tuple,
                 swarm_spd: tuple,
                 swarm_cd: float,
                 swarm_shot_order: tuple,
                 swarm_rot_amp: int,
                 swarm_rot_spd: int,
                 swarm_down_spd: int,
                 acolyte: bool,
                 ):
        self.alien_types = alien_types
        self.swarm_spd = swarm_spd
        self.alien_in_line = alien_in_line
        self.swarm_cd = swarm_cd
        self.swarm_shot_order = swarm_shot_order
        self.swarm_rot_amp = swarm_rot_amp
        self.swarm_rot_spd = swarm_rot_spd
        self.swarm_down_spd = swarm_down_spd
        self.acolyte = acolyte


LEVELS = [
    None,
    LevelSettings(8, (2, 2, 1, 1), (30, 250), 3.0, (0, 0, 1, 0, 1, 2, 0, 1), 0, 0, 50, False),
    LevelSettings(8, (3, 2, 2, 1, 1), (40, 320), 2.5, (0, 1, 2, 0, 1, 2, 0, 1), 0, 0, 60, False),
    LevelSettings(8, (3, 3, 3, 2, 2, 1), (50, 340), 2.0, (1, 0, 1, 2, 1, 2, 0, 1), 0, 0, 70, False),
    LevelSettings(8, (7, 3, 3, 2, 1), (50, 350), 2.0, (1, 0, 2, 1, 1, 1, 0, 2), 0, 0, 80, False),
    LevelSettings(8, (7, 3, 3, 2, 2), (60, 360), 1.8, (1, 1, 2, 1, 1, 1, 2, 1), 0, 0, 70, True),
    LevelSettings(5, (3, 3, 2, 2, 1, 1), (70, 380), 1.6, (0, 1, 2, 1, 2, 0, 1, 2), 20, 4, 60, True),
    LevelSettings(5, (7, 3, 3, 2, 2, 2), (70, 400), 1.5, (1, 1, 2, 2, 1, 1, 2, 1), 40, 5, 90, False),
]
