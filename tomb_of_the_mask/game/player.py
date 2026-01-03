import pygame
import game.settings
from game.level import is_wall, has_coin, collect_coin, is_exit, has_crystal, collect_crystal, has_spike, has_life, collect_life

class Player:
    def __init__(self, row, col, current_lives=None, game_scene=None):
        self.row = row
        self.col = col
        self.game_scene = game_scene
        ts = game.settings.TILE_SIZE
        self.x = col * ts
        self.y = row * ts
        self.dx = 0
        self.dy = 0
        self.is_moving = False
        self.speed = ts / 4
        self.coins = 0
        self.on_exit = False
        self.level_transitioning = False 
        
        # Таймер спеціального імунітету після Зеленого Порталу
        self.invulnerable_to_lava = 0 
    
        if current_lives is not None:
            self._lives = current_lives
        else:
            self._lives = game.settings.PLAYER_START_LIVES
            
        # Таймер стандартного імунітету після отримання шкоди (миготіння)
        self.invulnerable_timer = 0

    @property
    def lives(self):
        return self._lives
    
    @lives.setter
    def lives(self, value):
        self._lives = max(0, value)

    def take_damage(self):
        """Наносить шкоду, якщо немає загального імунітету (після удару)."""
        if self.invulnerable_timer == 0:
            self.lives -= 1
            self.invulnerable_timer = 60 # 1 секунда невразливості після удару
            if self.game_scene:
                self.game_scene.play_damage_sound()

    def set_lava_invulnerable(self, frames=120):
        """Вмикає захист від лави (наприклад, після телепортації)."""
        self.invulnerable_to_lava = frames

    def check_obstacle(self, r, c):
        if is_wall(r, c): return 1
        if has_spike(r, c): return 2
        return 0

    def update_timers(self):
        """Оновлює всі таймери імунітету."""
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.invulnerable_to_lava > 0:
            self.invulnerable_to_lava -= 1

    def handle_input(self, keys):
        if self.is_moving: return
        if self.lives <= 0: return

        if keys[pygame.K_UP]:    self.dx, self.dy = 0, -1
        elif keys[pygame.K_DOWN]:  self.dx, self.dy = 0, 1
        elif keys[pygame.K_LEFT]:  self.dx, self.dy = -1, 0
        elif keys[pygame.K_RIGHT]: self.dx, self.dy = 1, 0
        else: return

        target_r = self.row + self.dy
        target_c = self.col + self.dx
        
        obstacle = self.check_obstacle(target_r, target_c)
        if obstacle != 0:
            # Логіка удару об стіну/лаву БЕЗ руху
            if obstacle == 2: # Лава/Шип
                # Наносимо шкоду, ТІЛЬКИ якщо немає спец. імунітету від порталу
                if self.invulnerable_to_lava <= 0:
                    self.take_damage()
            return

        self.is_moving = True
        self.on_exit = False
        if self.game_scene:
            self.game_scene.play_jump_sound()

    def update(self):
        ts = game.settings.TILE_SIZE
        
        # Оновлення таймера після удару (миготіння) перенесено в update_timers,
        # але для безпеки можна залишити і тут, якщо update_timers не викликається окремо
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        current_row = int((self.y + ts / 2) / ts)
        current_col = int((self.x + ts / 2) / ts)

        # 1. Збір монет
        if has_coin(current_row, current_col):
            collect_coin(current_row, current_col)
            self.coins += 1

        # 2. Збір кристалів
        if has_crystal(current_row, current_col):
            collect_crystal(current_row, current_col)
            if self.game_scene:
                try: self.game_scene.play_krystal_sound()
                except: pass

        # 3. Перевірка лави під час руху (проходження крізь лаву)
        if has_spike(current_row, current_col):
            # Шкода, якщо немає імунітету від порталу
            if self.invulnerable_to_lava <= 0:
                self.take_damage()
            
        # 4. Збір життів
        if has_life(current_row, current_col):
            if self.lives < 3:
                collect_life(current_row, current_col)
                self.lives += 1
                if self.game_scene:
                    try: self.game_scene.play_heart_sound()
                    except: pass

        # Логіка виходу
        if is_exit(current_row, current_col):
            self.on_exit = True
        elif self.is_moving:
            self.on_exit = False

        if not self.is_moving:
            self.on_exit = is_exit(self.row, self.col)
            return

        # Фізика руху
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        next_col = int(self.x / ts)
        next_row = int(self.y / ts)
        
        obstacle = self.check_obstacle(next_row + self.dy, next_col + self.dx)

        if obstacle != 0:
            # Зупинка перед перешкодою
            self.row = next_row
            self.col = next_col
            self.x = self.col * ts
            self.y = self.row * ts
            self.is_moving = False
            self.on_exit = is_exit(self.row, self.col)
            
            # Удар об лаву при зупинці
            if obstacle == 2:
                if self.invulnerable_to_lava <= 0:
                    self.take_damage()

    def draw(self, screen, offset_x, offset_y):
        ts = game.settings.TILE_SIZE
        
        # Ефект миготіння при отриманні шкоди
        if self.invulnerable_timer > 0:
            if (self.invulnerable_timer // 4) % 2 == 0: return

        current_idx = game.settings.CURRENT_SKIN_INDEX
        try:
            skin_color = game.settings.SKINS[current_idx]["color"]
        except IndexError:
            skin_color = (255, 220, 100) # Fallback color
        if self.invulnerable_to_lava > 0:
            pygame.draw.rect(screen, (255, 255, 255), 
                           (offset_x + self.x - 2, offset_y + self.y - 2, ts + 4, ts + 4), 2)

        pygame.draw.rect(screen, skin_color, (offset_x + self.x, offset_y + self.y, ts, ts))