import pygame
import game.settings
from game.settings import WIDTH, HEIGHT
import os

class LobbyScene:
    def __init__(self):
        self.next_scene = None
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.text_font = pygame.font.SysFont("arial", 28)
        self.ui_font = pygame.font.SysFont("arial", 24)
        self.menu_items = [
            ("START GAME", "game"),
            ("SKINS SHOP", "shop"),
            ("SETTINGS", "settings"),
        ]
        self.selected_index = 0
        self.music_started = False
        self.click = None
        self.music_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "sounds",
            "lobby.mp3",
        )
        self.click_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "sounds",
            "klick.mp3",
        )
        try:
            if os.path.exists(self.click_path):
                self.click = pygame.mixer.Sound(self.click_path)
                self.click.set_volume(game.settings.SFX_VOLUME)
        except Exception:
            self.click = None
        self._start_music()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass
            elif event.key == pygame.K_RETURN:
                _, action = self.menu_items[self.selected_index]
                if action == "game":
                    self._stop_music()
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass
                self.next_scene = action

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 30))

        title = self.title_font.render("TOMB OF THE MASK", True, (255, 215, 120))
        title_shadow = self.title_font.render("TOMB OF THE MASK", True, (100, 50, 0))
        screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 37)))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        hint = self.text_font.render("ARROWS TO SELECT, ENTER TO START", True, (180, 180, 190))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        base_y = HEIGHT // 2 + 70
        for i, (label, _) in enumerate(self.menu_items):
            is_selected = i == self.selected_index
            color = (255, 215, 120) if is_selected else (220, 220, 220)
            text = self.text_font.render(label, True, color)
            x = WIDTH // 2
            y = base_y + i * 40
            screen.blit(text, text.get_rect(center=(x, y)))
            if is_selected:
                marker = self.text_font.render(">", True, (255, 215, 120))
                screen.blit(marker, marker.get_rect(center=(x - 120, y)))
        self.draw_crystal_ui(screen)

    def draw_crystal_ui(self, screen):
        amount = game.settings.TOTAL_CRYSTALS
        text_surf = self.ui_font.render(str(amount), True, (255, 255, 255))
        
        box_width = text_surf.get_width() + 50
        box_height = 36
        x = WIDTH - box_width - 20
        y = 20

        pygame.draw.rect(screen, (30, 30, 40), (x, y, box_width, box_height), border_radius=18)
        pygame.draw.rect(screen, (60, 60, 70), (x, y, box_width, box_height), width=2, border_radius=18)

        icon_cx = x + 20
        icon_cy = y + box_height // 2
        r = 8
        points = [
            (icon_cx, icon_cy - r - 2),
            (icon_cx + r, icon_cy),
            (icon_cx, icon_cy + r + 2),
            (icon_cx - r, icon_cy)
        ]
        pygame.draw.polygon(screen, (0, 255, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)

        screen.blit(text_surf, (x + 40, y + (box_height - text_surf.get_height()) // 2))

    def _start_music(self):
        if self.music_started:
            return
        try:
            if pygame.mixer.music.get_busy():
                return
        except Exception:
            pass
        if not os.path.exists(self.music_path):
            return
        try:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(game.settings.MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
            self.music_started = True
        except Exception:
            pass
    def _stop_music(self):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass
        self.music_started = False
