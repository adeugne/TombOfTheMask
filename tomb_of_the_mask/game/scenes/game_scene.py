import pygame
import random
import game.settings
from game.player import Player
from game.bat import Bat
import game.level as level_module
from game.level import draw_level, get_offsets
from game.level_generator import generate_level


class GameScene:
    def __init__(self):
        self.next_scene = None
        self.level_number = 1
        self.base_rows = 15
        self.base_cols = 9
        self.default_tile_size = 40 

        self.levels_until_crystal = random.randint(5, 7)
        self.waiting_to_start = True
        self.game_over = False
        self.total_coins = 0
        self.player = None
        self.bats = []

        self.start_new_level()

        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.title_font = pygame.font.SysFont("arial", 32, bold=True)
        self.info_font = pygame.font.SysFont("arial", 20)
        self.hint_font = pygame.font.SysFont("arial", 18)

    def start_new_level(self):
        saved_lives = None
        if self.player is not None:
            saved_lives = self.player.lives

        difficulty_tier = (self.level_number - 1) // 3
        new_rows = min(35, self.base_rows + (difficulty_tier * 2))
        new_cols = min(21, self.base_cols + (difficulty_tier * 2))

        screen_w = game.settings.WIDTH
        screen_h = game.settings.HEIGHT
        available_h = screen_h - 120
        available_w = screen_w - 20
        max_tile_w = available_w // new_cols
        max_tile_h = available_h // new_rows
        new_tile_size = min(self.default_tile_size, max_tile_w, max_tile_h)
        
        game.settings.TILE_SIZE = new_tile_size
        level_module.ROWS = new_rows
        level_module.COLS = new_cols

        spawn_crystal = False
        self.levels_until_crystal -= 1
        if self.levels_until_crystal <= 0:
            spawn_crystal = True
            self.levels_until_crystal = random.randint(5, 7)

        (level_module.LEVEL_MAP, level_module.SPAWN_ROW, level_module.SPAWN_COL) = \
            generate_level(new_rows, new_cols, spawn_crystal=spawn_crystal)

        self.bats = []
        new_map = []
        for r, row_str in enumerate(level_module.LEVEL_MAP):
            row_chars = list(row_str)
            for c, char in enumerate(row_chars):
                if char == 'B':
                    # 👇 Передаємо поточний рівень
                    self.bats.append(Bat(r, c, current_level=self.level_number))
                    row_chars[c] = '0' 
            new_map.append("".join(row_chars))
        
        level_module.LEVEL_MAP = new_map

        self.total_coins = sum(row.count("C") for row in level_module.LEVEL_MAP)

        self.player = Player(
            level_module.SPAWN_ROW, 
            level_module.SPAWN_COL, 
            current_lives=saved_lives
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key == pygame.K_RETURN:
                    self.__init__() 
                elif event.key == pygame.K_ESCAPE:
                    self.next_scene = "lobby"
                return

            if event.key == pygame.K_ESCAPE:
                self.next_scene = "lobby"
                game.settings.TILE_SIZE = self.default_tile_size
            
            if self.waiting_to_start:
                if event.key == pygame.K_RETURN:
                    self.waiting_to_start = False
                return 

    def update(self, dt):
        if self.waiting_to_start or self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()
        
        player_rect = pygame.Rect(self.player.x + 4, self.player.y + 4, 
                                  game.settings.TILE_SIZE - 8, game.settings.TILE_SIZE - 8)
        
        for bat in self.bats:
            bat.update()
            if player_rect.colliderect(bat.rect):
                self.player.take_damage()

        if self.player.lives <= 0:
            self.game_over = True

        if self.player.on_exit:
            coins_left = any("C" in row for row in level_module.LEVEL_MAP)
            if not coins_left:
                self.level_number += 1
                self.start_new_level()

    def draw(self, screen):
        screen.fill((95, 95, 125))

        coins_current = sum(row.count("C") for row in level_module.LEVEL_MAP)
        coins_collected = self.total_coins - coins_current
        exit_is_open = (coins_current == 0)

        draw_level(screen, active_exit=exit_is_open)
        offset_x, offset_y = get_offsets(screen)
        
        for bat in self.bats:
            bat.draw(screen, offset_x, offset_y)
            
        self.player.draw(screen, offset_x, offset_y)
        
        coin_text = self.font.render(f"Coins: {coins_collected}/{self.total_coins}", True, (255, 215, 0))
        screen.blit(coin_text, (15, 15))

        level_text = self.title_font.render(f"Level {self.level_number}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(screen.get_width() // 2, 25))
        screen.blit(level_text, level_rect)

        self.draw_crystal_ui(screen)
        
        heart_text = self.font.render(f"Lives: {'♥' * self.player.lives}", True, (255, 50, 50))
        screen.blit(heart_text, (15, 45))

        hint = self.hint_font.render("LEAVE GAME - [ESC]", True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 15)))

        if self.game_over:
            self.draw_game_over(screen)
        elif self.waiting_to_start:
            self.draw_popup(screen)

    def draw_crystal_ui(self, screen):
        amount = game.settings.TOTAL_CRYSTALS
        text_surf = self.font.render(str(amount), True, (255, 255, 255))
        box_width = text_surf.get_width() + 50
        box_height = 36
        x = screen.get_width() - box_width - 15
        y = 10
        pygame.draw.rect(screen, (30, 30, 40), (x, y, box_width, box_height), border_radius=18)
        pygame.draw.rect(screen, (60, 60, 70), (x, y, box_width, box_height), width=2, border_radius=18)
        
        icon_cx = x + 20
        icon_cy = y + box_height // 2
        r = 8
        points = [(icon_cx, icon_cy - r - 2), (icon_cx + r, icon_cy), (icon_cx, icon_cy + r + 2), (icon_cx - r, icon_cy)]
        pygame.draw.polygon(screen, (0, 255, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        screen.blit(text_surf, (x + 40, y + (box_height - text_surf.get_height()) // 2))

    def draw_popup(self, screen):
        self._draw_centered_box(screen, "ЗБЕРИ ВСІ МОНЕТИ!", "Щоб відкрити портал", "[ ENTER ] Старт")

    def draw_game_over(self, screen):
        self._draw_centered_box(screen, "ГРА ЗАВЕРШЕНА", "Життя скінчились :(", "[ ENTER ] Спочатку   [ ESC ] Меню", border_color=(255, 50, 50))

    def _draw_centered_box(self, screen, title_txt, sub_txt, hint_txt, border_color=(255, 215, 0)):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        screen.blit(overlay, (0, 0))

        center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
        box_w, box_h = 340, 180
        
        pygame.draw.rect(screen, (40, 30, 40), (center_x - box_w//2, center_y - box_h//2, box_w, box_h), border_radius=15)
        pygame.draw.rect(screen, border_color, (center_x - box_w//2, center_y - box_h//2, box_w, box_h), width=3, border_radius=15)

        t1 = self.title_font.render(title_txt, True, (255, 255, 255))
        t2 = self.info_font.render(sub_txt, True, (200, 200, 200))
        t3 = self.info_font.render(hint_txt, True, (255, 255, 100))

        screen.blit(t1, t1.get_rect(center=(center_x, center_y - 40)))
        screen.blit(t2, t2.get_rect(center=(center_x, center_y)))
        screen.blit(t3, t3.get_rect(center=(center_x, center_y + 50)))