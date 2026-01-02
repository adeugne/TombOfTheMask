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
                pygame.draw.rect(screen, (95, 95, 125), (x, y, ts, ts))
            elif tile == "S":
                pygame.draw.rect(screen, (50, 40, 40), (x, y, ts, ts))
                spike_color = (220, 50, 50)
                m = ts // 5
                cx, cy = x + ts//2, y + ts//2
                points = [(cx, y + m), (x + ts - m, cy), (cx, y + ts - m), (x + m, cy)]
                pygame.draw.polygon(screen, spike_color, points)
                pygame.draw.polygon(screen, (100, 0, 0), points, 2)
            else:
                pygame.draw.rect(screen, (10, 10, 20), (x, y, ts, ts))

            if tile == "C":
                pygame.draw.circle(screen, (255, 215, 0), (x + ts // 2, y + ts // 2), ts // 6)
            if tile == "K":
                cx, cy = x + ts // 2, y + ts // 2
                size = ts // 4
                points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
                pygame.draw.polygon(screen, (0, 255, 255), points)
                pygame.draw.polygon(screen, (255, 255, 255), points, 1)
            if tile == "E":
                border = max(2, ts // 8)
                color = (100, 255, 100) if active_exit else (255, 140, 0)
                pygame.draw.rect(screen, color, (x + border, y + border, ts - border*2, ts - border*2), border_radius=border)