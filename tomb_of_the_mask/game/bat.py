import pygame
import random
import game.settings
from game.level import is_wall, has_spike

class Bat:
    def __init__(self, row, col, current_level=1):
        self.row = row
        self.col = col
        ts = game.settings.TILE_SIZE
        
        self.x = col * ts
        self.y = row * ts
        
        padding = 10 
        self.rect = pygame.Rect(self.x + padding, self.y + padding, ts - padding*2, ts - padding*2)
        
        self.dx = 0
        self.dy = 0
        
        # 1. Сканування простору (ТІЛЬКИ ГОРИЗОНТАЛЬ)
        h_space = 1
        c = col - 1
        while not is_wall(row, c): h_space += 1; c -= 1
        c = col + 1
        while not is_wall(row, c): h_space += 1; c += 1
            
        # 2. Логіка: Завжди горизонтально
        self.axis = 'horizontal'
        self.flight_range = h_space

        # 3. Швидкість
        base_speed = 1.2
        range_bonus = 0.3 if self.flight_range > 8 else 0
        level_bonus = 0
        if current_level > 20:
            level_bonus = min(1.5, (current_level - 20) * 0.05)
            
        final_speed = base_speed + range_bonus + level_bonus
        
        direction = random.choice([-1, 1])
        self.dx = final_speed * direction
        self.dy = 0 
            
        self.wing_state = 0
        self.animation_speed = 0.12

    def update(self):
        ts = game.settings.TILE_SIZE
        
        next_x = self.x + self.dx
        
        # Перевірка стін
        check_x = next_x + ts if self.dx > 0 else next_x
        margin = 2
        if self.dx > 0: check_x -= margin
        elif self.dx < 0: check_x += margin

        col_check = int(check_x / ts)
        row_check = int(self.y / ts)
        
        # Check for walls and lava
        if is_wall(row_check, col_check) or has_spike(row_check, col_check):
            self.dx *= -1
        else:
            self.x = next_x
        
        self.rect.x = int(self.x + 10)
        self.rect.y = int(self.y + 10)
            
        self.wing_state += self.animation_speed
        if self.wing_state > 3:
            self.wing_state = 0

    def draw(self, screen, offset_x, offset_y):
        ts = game.settings.TILE_SIZE
        draw_x = offset_x + self.x
        draw_y = offset_y + self.y
        center = (draw_x + ts // 2, draw_y + ts // 2)
        
        pygame.draw.circle(screen, (70, 20, 90), center, ts // 5)
        
        wing_y = 0
        state = int(self.wing_state)
        if state == 1: wing_y = -3
        elif state == 2: wing_y = 0
        elif state == 3: wing_y = 3
        
        wing_color = (100, 40, 120)
        
        for direction in [-1, 1]:
            pygame.draw.polygon(screen, wing_color, [
                (center[0] + (ts//5 * direction), center[1]),
                (center[0] + (ts//2 * direction), center[1] - ts//4 + wing_y),
                (center[0] + (ts//5 * direction), center[1] + ts//6)
            ])
        
        pygame.draw.circle(screen, (255, 50, 50), (center[0] - 3, center[1] - 2), 2)
        pygame.draw.circle(screen, (255, 50, 50), (center[0] + 3, center[1] - 2), 2)