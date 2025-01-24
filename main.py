
import gc 
gc.disable()
import pygame
pygame.init()

from GameApp import GameApp
from MainMenu import MainMenu
from Lib import Engine
Engine.IgnoreScreenScaling()

state = 1
while True:
    if state == 1:
        state = MainMenu().run()
    elif state == 2:
        state = GameApp().run()
    else:
        break


pygame.quit()
