"""Scenes package for tomb_like_game."""

from .base_scene import BaseScene
from .lobby import LobbyScene
from .game_scene import GameScene
from .shop import ShopScene 

__all__ = ["BaseScene", "LobbyScene", "GameScene", "ShopScene"]