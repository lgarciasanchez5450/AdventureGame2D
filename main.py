
import gc 
gc.disable()
import pygame
pygame.init()

from GameApp import GameApp
from MainMenu import MainMenu

pygame.display.set_caption('Game Title')


state = 2
while True:
    if state == 1:
        state = MainMenu().run()
    elif state == 2:
        state = GameApp().run()
    else:
        break


pygame.quit()
