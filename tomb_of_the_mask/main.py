import pygame
from game.settings import WIDTH, HEIGHT, FPS, TITLE
from game.scenes.lobby import LobbyScene
from game.scenes.game_scene import GameScene
from game.scenes.shop import ShopScene
from game.scenes.settings_scene import SettingsScene

def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    scenes = {
        "lobby": LobbyScene,
        "game": GameScene,
        "shop": ShopScene,
        "settings": SettingsScene,
    }

    current_scene = LobbyScene()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            current_scene.handle_event(event)

        if hasattr(current_scene, 'exit_game') and current_scene.exit_game:
            running = False
            continue

        current_scene.update(dt)

        if current_scene.next_scene:
            scene_class = scenes[current_scene.next_scene]
            current_scene = scene_class()
            continue

        current_scene.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
