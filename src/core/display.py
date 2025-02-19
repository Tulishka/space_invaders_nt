import pygame


class DisplayManager:
    def __init__(self, game_screen_size: tuple[int, int], fullscreen_size: tuple[int, int] = None,
                 fullscreen_enabled: bool = False):
        self.all_display_modes = []
        self.game_screen_size = game_screen_size
        self.fullscreen_size = fullscreen_size
        self.fullscreen_enabled = fullscreen_enabled
        self.screen_surface: pygame.Surface | None = None

    def display_modes(self) -> list[tuple[int, int]]:
        if not self.all_display_modes:
            self.all_display_modes = sorted(
                mode for mode in pygame.display.list_modes(depth=0, flags=pygame.FULLSCREEN, display=0)
                if mode[0] >= self.game_screen_size[0] and mode[1] >= self.game_screen_size[1]
            )
        return self.all_display_modes

    def display_modes_titles(self) -> list[str]:
        return [f"{m[0]} x {m[1]}" for m in self.display_modes()]

    def desired_fullscreen_size(self) -> tuple[int, int] | None:
        if not self.fullscreen_enabled:
            return None

        return self.fullscreen_size or self.game_screen_size

    def set_mode(self, fullscreen_size: tuple[int, int] = None, fullscreen_enabled: bool = None):
        if fullscreen_size is not None:
            self.fullscreen_size = fullscreen_size
        if fullscreen_enabled is not None:
            self.fullscreen_enabled = fullscreen_enabled
        self.init_display()

    def init_display(self):
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        fullscreen_size = self.desired_fullscreen_size()
        if fullscreen_size:
            flags |= pygame.FULLSCREEN
        display = pygame.display.set_mode(fullscreen_size or self.game_screen_size, flags)

        if fullscreen_size is None or display.get_size() == self.game_screen_size:
            self.screen_surface = display
            return

        screen_rect = pygame.Rect(
            display.get_width() // 2 - self.game_screen_size[0] // 2,
            display.get_height() // 2 - self.game_screen_size[1] // 2,
            self.game_screen_size[0], self.game_screen_size[1]
        )
        self.screen_surface = display.subsurface(screen_rect)
