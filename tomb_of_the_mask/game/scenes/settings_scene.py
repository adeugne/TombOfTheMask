import pygame
import game.settings
from game.settings import WIDTH, HEIGHT


class SettingsScene:
    def __init__(self):
        self.next_scene = None
        self.title_font = pygame.font.SysFont("arial", 42, bold=True)
        self.text_font = pygame.font.SysFont("arial", 26)
        self.menu_items = [
            ("MUSIC VOLUME", "music_volume"),
            ("SFX VOLUME", "sfx_volume"),
            ("BACK", "back"),
        ]
        self.selected_index = 0
        self.step = 0.05
        import os
        music_path = os.path.join(
            game.settings.SOUNDS_PATH, "lobby.mp3",
        )
        try:
            if os.path.exists(music_path) and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(game.settings.MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass
        self.click = None
        try:
            click_path = os.path.join(
                game.settings.SOUNDS_PATH, "klick.mp3"
            )
            if os.path.exists(click_path):
                self.click = pygame.mixer.Sound(click_path)
                self.click.set_volume(game.settings.SFX_VOLUME)
        except pygame.error:
            self.click = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = "lobby"
                return
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                try:
                    if self.click:
                        self.click.play()
                except pygame.error:
                    pass
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                try:
                    if self.click:
                        self.click.play()
                except pygame.error:
                    pass
            elif event.key == pygame.K_LEFT:
                self._adjust_value(-self.step)
                try:
                    if self.click:
                        self.click.play()
                except pygame.error:
                    pass
            elif event.key == pygame.K_RIGHT:
                self._adjust_value(self.step)
                try:
                    if self.click:
                        self.click.play()
                except pygame.error:
                    pass
            elif event.key == pygame.K_RETURN:
                _, action = self.menu_items[self.selected_index]
                if action == "back":
                    self.next_scene = "lobby"
                    try:
                        if self.click:
                            self.click.play()
                    except pygame.error:
                        pass

    def _adjust_value(self, delta):
        _, action = self.menu_items[self.selected_index]
        if action == "music_volume":
            game.settings.MUSIC_VOLUME = self._clamp(game.settings.MUSIC_VOLUME + delta, max_val=0.25)
            try:
                pygame.mixer.music.set_volume(game.settings.MUSIC_VOLUME)
            except pygame.error:
                pass
        elif action == "sfx_volume":
            game.settings.SFX_VOLUME = self._clamp(game.settings.SFX_VOLUME + delta, max_val=0.25)
            try:
                if self.click:
                    self.click.set_volume(game.settings.SFX_VOLUME)
            except pygame.error:
                pass

    def _clamp(self, value, max_val=1.0):
        return max(0.0, min(max_val, value))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((18, 18, 26))
        title = self.title_font.render("SETTINGS", True, (255, 215, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 220)))

        base_y = HEIGHT // 2 - 90
        for i, (label, action) in enumerate(self.menu_items):
            y = base_y + i * 90
            is_selected = i == self.selected_index
            color = (255, 215, 120) if is_selected else (220, 220, 220)
            text = self.text_font.render(label, True, color)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))

            if action in ("music_volume", "sfx_volume"):
                value = game.settings.MUSIC_VOLUME if action == "music_volume" else game.settings.SFX_VOLUME
                self._draw_slider(screen, WIDTH // 2, y + 30, value, is_selected)

        hint = self.text_font.render("LEFT/RIGHT TO ADJUST, ESC TO BACK", True, (180, 180, 190))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def _draw_slider(self, screen, center_x, center_y, value, is_selected):
        width = 220
        height = 8
        x = center_x - width // 2
        y = center_y - height // 2
        track_color = (60, 60, 70)
        fill_color = (255, 140, 60) if is_selected else (200, 120, 50)
        display_value = min(1.0, value * 4)
        
        pygame.draw.rect(screen, track_color, (x, y, width, height), border_radius=4)
        pygame.draw.rect(screen, fill_color, (x, y, int(width * display_value), height), border_radius=4)
        knob_x = x + int(width * display_value)
        pygame.draw.circle(screen, (240, 240, 240), (knob_x, center_y), 6)
