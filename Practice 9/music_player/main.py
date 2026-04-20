import pygame
from player import run_player

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    run_player()
    pygame.quit()