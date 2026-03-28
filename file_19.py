import pygame
import sys
from settings import *

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Dungeon Blaster")
    pygame.mouse.set_visible(True)

    from menu import MainMenu, ControlsScreen, DeathScreen
    from game import Game

    clock = pygame.time.Clock()
    state = 'menu'
    game = None
    menu = MainMenu(screen)
    controls = None
    death = None

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        if state == 'menu':
            menu.update(dt)
            menu.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                result = menu.handle_event(event)
                if result == 'start_run':
                    game = Game(screen)
                    state = 'game'
                elif result == 'controls':
                    controls = ControlsScreen(screen)
                    state = 'controls'
                elif result == 'quit':
                    pygame.quit()
                    sys.exit()

        elif state == 'controls':
            controls.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                r = controls.handle_event(event)
                if r == 'back':
                    state = 'menu'
                    menu = MainMenu(screen)

        elif state == 'game':
            result = game.run()
            if result == 'quit':
                pygame.quit()
                sys.exit()
            elif result == 'menu':
                state = 'menu'
                menu = MainMenu(screen)
            elif result == 'dead':
                death = DeathScreen(screen, game)
                state = 'dead'

        elif state == 'dead':
            death.update(dt)
            death.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                r = death.handle_event(event)
                if r == 'restart':
                    game = Game(screen)
                    state = 'game'
                elif r == 'menu':
                    state = 'menu'
                    menu = MainMenu(screen)

if __name__ == '__main__':
    main()