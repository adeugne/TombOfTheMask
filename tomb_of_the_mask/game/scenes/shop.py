import pygame
import game.settings
from game.settings import WIDTH, HEIGHT
import os

class ShopScene:
    def __init__(self):
        self.next_scene = None
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.item_font = pygame.font.SysFont("arial", 28)
        self.price_font = pygame.font.SysFont("arial", 22)
        
        self.selected_index = game.settings.CURRENT_SKIN_INDEX
        self.scroll_offset = 0
        music_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "sounds",
            "lobby.mp3",
        )
        try:
            if os.path.exists(music_path) and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(game.settings.MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
        except Exception:
            pass
        self.click = None
        click_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "sounds",
            "klick.mp3",
        )
        try:
            if os.path.exists(click_path):
                self.click = pygame.mixer.Sound(click_path)
                self.click.set_volume(game.settings.SFX_VOLUME)
        except Exception:
            self.click = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = "lobby"
            
            if event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 0:
                    self.selected_index = len(game.settings.SKINS) - 1
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass
            
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index >= len(game.settings.SKINS):
                    self.selected_index = 0
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass

            if event.key == pygame.K_RETURN:
                self.try_buy_or_equip()
                try:
                    if self.click:
                        self.click.play()
                except Exception:
                    pass

    def try_buy_or_equip(self):
        skin = game.settings.SKINS[self.selected_index]
        price = skin["price"]
        
        if self.selected_index in game.settings.OWNED_SKINS:
            game.settings.CURRENT_SKIN_INDEX = self.selected_index
        elif game.settings.TOTAL_CRYSTALS >= price:
            game.settings.TOTAL_CRYSTALS -= price
            game.settings.OWNED_SKINS.append(self.selected_index)
            game.settings.CURRENT_SKIN_INDEX = self.selected_index 

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((15, 15, 20))

        title = self.title_font.render("SKIN SHOP", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

        self.draw_crystal_ui(screen)

        hint = self.price_font.render("[ESC] BACK    [ENTER] BUY / EQUIP", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

        start_y = 120
        item_height = 70
        
        for i, skin in enumerate(game.settings.SKINS):
            y_pos = start_y + i * item_height
            if y_pos > HEIGHT - 80: continue

            is_selected = (i == self.selected_index)
            is_owned = (i in game.settings.OWNED_SKINS)
            is_equipped = (i == game.settings.CURRENT_SKIN_INDEX)

            bg_color = (40, 40, 50) if is_selected else (25, 25, 30)
            pygame.draw.rect(screen, bg_color, (50, y_pos, WIDTH - 100, 60), border_radius=10)

            if is_selected:
                pygame.draw.rect(screen, (255, 215, 0), (50, y_pos, WIDTH - 100, 60), width=2, border_radius=10)

            pygame.draw.rect(screen, skin["color"], (70, y_pos + 15, 30, 30))

            name_color = (255, 255, 255) if is_owned else (150, 150, 150)
            name_text = self.item_font.render(skin["name"], True, name_color)
            screen.blit(name_text, (120, y_pos + 15))

            if is_equipped:
                status_text = self.price_font.render("EQUIPPED", True, (0, 255, 0))
                screen.blit(status_text, (WIDTH - 70 - status_text.get_width(), y_pos + 20))
            elif is_owned:
                status_text = self.price_font.render("OWNED", True, (100, 200, 100))
                screen.blit(status_text, (WIDTH - 70 - status_text.get_width(), y_pos + 20))
            else:
                can_afford = game.settings.TOTAL_CRYSTALS >= skin["price"]
                price_color = (0, 255, 255) if can_afford else (200, 50, 50)

                price_str = str(skin['price'])
                price_surf = self.price_font.render(price_str, True, price_color)
                
                icon_cx = WIDTH - 80
                icon_cy = y_pos + 30
                text_x = icon_cx - 15 - price_surf.get_width()
                text_y = y_pos + (60 - price_surf.get_height()) // 2
                
                screen.blit(price_surf, (text_x, text_y))
                self.draw_crystal_icon(screen, icon_cx, icon_cy, 6, (0, 255, 255))

    def draw_crystal_ui(self, screen):
        amount = game.settings.TOTAL_CRYSTALS
        text_surf = self.item_font.render(str(amount), True, (255, 255, 255))
        
        box_width = text_surf.get_width() + 50
        box_height = 36
        x = WIDTH - box_width - 20
        y = 20

        pygame.draw.rect(screen, (30, 30, 40), (x, y, box_width, box_height), border_radius=18)
        pygame.draw.rect(screen, (60, 60, 70), (x, y, box_width, box_height), width=2, border_radius=18)

        self.draw_crystal_icon(screen, x + 20, y + box_height // 2, 8, (0, 255, 255))
        screen.blit(text_surf, (x + 40, y + (box_height - text_surf.get_height()) // 2))

    def draw_crystal_icon(self, screen, cx, cy, r, color):
        points = [
            (cx, cy - r - 2),
            (cx + r, cy),
            (cx, cy + r + 2),
            (cx - r, cy)
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)