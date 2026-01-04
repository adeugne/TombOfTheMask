import os

WIDTH, HEIGHT = 480, 750
FPS = 60

TITLE = "Tomb Of The Mask"
BG_COLOR = (15, 15, 20)
TILE_SIZE = 40
TOTAL_CRYSTALS = 0

PLAYER_START_LIVES = 3

MUSIC_VOLUME = 0.064 
SFX_VOLUME = 0.1        
LOBBY_VOLUME = MUSIC_VOLUME
GAME_VOLUME = MUSIC_VOLUME

CURRENT_SKIN_INDEX = 0
OWNED_SKINS = [0]

SKINS = [
    {"name": "CLASSIC",   "price": 0,   "color": (255, 220, 100)},
    {"name": "RED NEON",  "price": 1,   "color": (255, 50, 50)},
    {"name": "ICY BLUE",  "price": 3,   "color": (0, 200, 255)},
    {"name": "TOXIC",     "price": 5,   "color": (100, 255, 50)},
    {"name": "VIOLET",    "price": 10,  "color": (200, 50, 255)},
    {"name": "GHOST",     "price": 15,  "color": (200, 200, 220)},
    {"name": "GOLDEN",    "price": 20,  "color": (255, 215, 0)},
    {"name": "DARKNESS",  "price": 35,  "color": (50, 50, 50)},
]

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_PATH = os.path.join(ROOT_PATH, "sounds")