import pygame
import sys
from ui import SynthUI


def main():
    pygame.init()
    ui = SynthUI()
    ui.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
