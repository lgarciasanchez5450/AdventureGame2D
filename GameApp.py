from pygame import display
import pygame.constants as const
from pygame.time import Clock
import time
import pygame
pygame.font.init()
from Application.Fonts import *
# from GuiFramework import Input
import moderngl as mgl
from Scene import RasterScene,RayTraceScene
from Scripts.ProgramManager import ProgramManager
from Utils.debug import Tracer
from Utils.events import EventChannel
class Engine:
    def __init__(self) -> None:
        # MGL context
        self.ctx = mgl.create_context(standalone=True) #Headless Context

        # Time variables
        self.clock = Clock()
        self.time = Time()
        self.tracer = Tracer()


        self.event_channel = EventChannel()
        # Project handler
        self.program_manager = ProgramManager(self.ctx)
        self.scenes:dict[str,RayTraceScene] = {'scene1':RayTraceScene(self)}
        self.active_scene:RayTraceScene = list(self.scenes.values())[0]
        self.running = False

    def start(self):
        # rss_base = psutil.Process().memory_info().rss #memory(rss from psutil) used by python only importing python and moderngl

        # pygame.display.set_caption(f'{self.active_scene.get_memory()/1_000_000:.2f} MB')
        # pygame.display.set_caption(f'{(psutil.Process().memory_info().rss-rss_base)/1_000_000} MB')
        self.running = True 
        self.time.start()
        self.active_scene.start()
        while self.running:
            for event in pygame.event.get():
                if event.type == const.QUIT:
                    self.running = False
                elif event.type== const.KEYDOWN:
                    if event.key == const.K_p:
                        self.tracer.running = True
                elif event.type== const.KEYUP:
                    if event.key == const.K_p:
                        self.tracer.running = False

                self.event_channel.fire(event)

            self.time.update()
            self.active_scene.update()
            self.active_scene.draw(pygame.display.get_surface())
            display.flip()
            self.clock.tick(60)
        self.tracer.show()


        
class Time:
    __slots__ = 'dt','fixedDt','_prevTime','time','timeScale','realTime','_startTime','unscaledDeltaTime','frame'
    def __init__(self) -> None:
        self.dt = 0
        self.timeScale = 1
        self.fixedDt = 0.1


    def start(self):
        self.time = 0
        self.realTime = 0
        self.unscaledDeltaTime = 0
        self.frame = 0
        self._prevTime = self._startTime = time.perf_counter()

    
    def update(self):
        t = time.perf_counter()
        u = self.unscaledDeltaTime = (t - self._prevTime)
        self.dt = u * self.timeScale
        self.time += self.dt
        self._prevTime = t
        self.realTime = t - self._startTime
        self.frame += 1

    def getFPS(self):
        return 1 / self.unscaledDeltaTime if self.unscaledDeltaTime else 0

class GameApp: 
    def __init__(self) -> None:
        self.engine = Engine()  
    
    def run(self):
        self.screen = pygame.display.set_mode((800,600),const.RESIZABLE)
        return self.engine.start()
   
        
if __name__ == '__main__':
    GameApp().run()
