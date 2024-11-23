
import gc 
gc.disable()
import pygame
pygame.init()

from GameApp import GameApp
from MainMenu import MainMenu
import Window

window = Window.window = Window.Window((500,500))
pygame.display.set_caption('Game Title')


state = 1
while True:
    if state == 1:
        state = MainMenu().run()
    elif state == 2:
        state = GameApp().run()
    else:
        break


pygame.quit()
window.close()