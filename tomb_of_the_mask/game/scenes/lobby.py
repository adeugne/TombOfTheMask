import pygame
import game.settings
from game.settings import WIDTH, HEIGHT

class LobbyScene:
    def __init__(self):
        self.next_scene = None
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.text_font = pygame.font.SysFont("arial", 28)
        self.ui_font = pygame.font.SysFont("arial", 24)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.next_scene = "game"
            if event.key == pygame.K_s:
                self.next_scene = "shop"

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 30))

        title = self.title_font.render("TOMB OF THE MASK", True, (255, 215, 120))
        title_shadow = self.title_font.render("TOMB OF THE MASK", True, (100, 50, 0))
        screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 37)))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        hint_start = self.text_font.render("[ ENTER ] START GAME", True, (220, 220, 220))
        hint_shop = self.text_font.render("[ S ] OPEN SKINS SHOP", True, (255, 215, 0))

        screen.blit(hint_start, hint_start.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
        screen.blit(hint_shop, hint_shop.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))
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