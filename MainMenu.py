from Lib.GuiFramework import *
from pygame import event
ExitMainMenuEvent = event.Event(event.custom_type())

class MainMenu: 
    def __init__(self) -> None:
        if pygame.display.get_active()==0:
            self.screen = pygame.display.set_mode((500,500))
        pygame.display.set_caption('Main Menu')
        self.base_layer = Layer(display.get_window_size())
        self.base_layer.space.addObjects(
            BackgroundColor((0,50,50)),
            Aligner(
                AddText(
                    Button((0,0),(50,50),ColorScheme(100,100,100),lambda : event.post(ExitMainMenuEvent)),
                    'Start',(255,255,255),font.SysFont('Arial',20)
                ),
                0.5,0.5
            ),
            Aligner(
                Text((0,0),'Game Title',(255,255,255),font.SysFont('Arial',50)),
                0.5,0.2
            )
        )

    def run(self):
        while True:
            input = getInput()
            if input.quitEvent:
                return self.close(0)
            elif ExitMainMenuEvent.type in input.Events:
                return self.close(2)
            self.base_layer.update(input)
            self.base_layer.draw(pygame.display.get_surface())
            Clock().tick(30)
            pygame.display.flip()

    def close(self,ret_code:int):
        self.base_layer.space.clear()
        return ret_code
    

if __name__ == '__main__':
    print('Exit Status:',MainMenu().run())