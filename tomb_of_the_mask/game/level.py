import pygame
import game.settings
from game.level_generator import generate_level

ROWS = 15
COLS = 9
LEVEL_MAP, SPAWN_ROW, SPAWN_COL = generate_level(ROWS, COLS)

def is_wall(row, col):
    if row < 0 or col < 0: return True
    if row >= len(LEVEL_MAP) or col >= len(LEVEL_MAP[0]): return True
    return LEVEL_MAP[row][col] == "1"

def has_coin(row, col):
    if not (0 <= row < len(LEVEL_MAP) and 0 <= col < len(LEVEL_MAP[0])): return False
    return LEVEL_MAP[row][col] == "C"

def has_crystal(row, col):
    if not (0 <= row < len(LEVEL_MAP) and 0 <= col < len(LEVEL_MAP[0])): return False
    return LEVEL_MAP[row][col] == "K"

def has_life(row, col):
    if not (0 <= row < len(LEVEL_MAP) and 0 <= col < len(LEVEL_MAP[0])): return False
    return LEVEL_MAP[row][col] == "L"

def has_spike(row, col):
    if not (0 <= row < len(LEVEL_MAP) and 0 <= col < len(LEVEL_MAP[0])): return False
    return LEVEL_MAP[row][col] == "S"

def collect_coin(row, col):
    global LEVEL_MAP
    if has_coin(row, col):
        row_list = list(LEVEL_MAP[row])
        row_list[col] = "0"
        LEVEL_MAP[row] = "".join(row_list)

def collect_crystal(row, col):
    global LEVEL_MAP
    if has_crystal(row, col):
        row_list = list(LEVEL_MAP[row])
        row_list[col] = "0"
        LEVEL_MAP[row] = "".join(row_list)
        game.settings.TOTAL_CRYSTALS += 1

def collect_life(row, col):
    global LEVEL_MAP
    if has_life(row, col):
        row_list = list(LEVEL_MAP[row])
        row_list[col] = "0"
        LEVEL_MAP[row] = "".join(row_list)

def is_exit(row, col):
    if not (0 <= row < len(LEVEL_MAP) and 0 <= col < len(LEVEL_MAP[0])): return False
    return LEVEL_MAP[row][col] == "E"

def get_offsets(screen):
    ts = game.settings.TILE_SIZE
    rows = len(LEVEL_MAP)
    cols = len(LEVEL_MAP[0])
    map_width = cols * ts
    map_height = rows * ts
    screen_width, screen_height = screen.get_size()
    offset_x = (screen_width - map_width) // 2
    offset_y = (screen_height - map_height) // 2
    return offset_x, offset_y

def draw_level(screen, active_exit=False):
    ts = game.settings.TILE_SIZE
    offset_x, offset_y = get_offsets(screen)

    for r, row in enumerate(LEVEL_MAP):
        for c, tile in enumerate(row):
            x = offset_x + c * ts
            y = offset_y + r * ts

            if tile == "1":
                # Звичайна стіна
                pygame.draw.rect(screen, (95, 95, 125), (x, y, ts, ts))
            
            elif tile == "S":
                # ЛАВОВА СТІНА (Колишній шип)
                pygame.draw.rect(screen, (40, 20, 20), (x, y, ts, ts))
                lava_color = (255, 80, 0)
                core_color = (255, 200, 50)
                cx, cy = x + ts // 2, y + ts // 2
                points = [
                    (x + 2, cy), (x + ts//4, cy - 2), 
                    (cx, cy + 2), (x + 3*ts//4, cy - 2), (x + ts - 2, cy)
                ]
                pygame.draw.lines(screen, lava_color, False, points, 3)
                points_v = [
                    (cx, y + 2), (cx - 2, y + ts//4), 
                    (cx + 2, cy), (cx - 2, y + 3*ts//4), (cx, y + ts - 2)
                ]
                pygame.draw.lines(screen, lava_color, False, points_v, 3)
                pygame.draw.circle(screen, core_color, (cx, cy), 3)

            else:
                # Підлога
                pygame.draw.rect(screen, (10, 10, 20), (x, y, ts, ts))

            if tile == "C":
                pygame.draw.circle(screen, (255, 215, 0), (x + ts // 2, y + ts // 2), ts // 6)
            
            if tile == "K":
                cx, cy = x + ts // 2, y + ts // 2
                size = ts // 4
                points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
                pygame.draw.polygon(screen, (0, 255, 255), points)
                pygame.draw.polygon(screen, (255, 255, 255), points, 1)
            
            if tile == "L":
                cx, cy = x + ts // 2, y + ts // 2
                color = (255, 50, 50)
                r_heart = ts // 4
                pygame.draw.circle(screen, color, (cx - r_heart//2, cy - r_heart//2), r_heart//2)
                pygame.draw.circle(screen, color, (cx + r_heart//2, cy - r_heart//2), r_heart//2)
                triangle_pts = [
                    (cx - r_heart, cy - r_heart//4),
                    (cx + r_heart, cy - r_heart//4),
                    (cx, cy + r_heart)
                ]
                pygame.draw.polygon(screen, color, triangle_pts)

            if tile == "E":
                border = max(2, ts // 8)
                color = (100, 255, 100) if active_exit else (255, 140, 0)
                pygame.draw.rect(screen, color, (x + border, y + border, ts - border*2, ts - border*2), border_radius=border)
