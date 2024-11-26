from pygame import display
import pygame.constants as const
from pygame.time import Clock
import pygame
from Application.Fonts import *
# from GuiFramework import Input

from SceneTransitions.BaseTransition import BaseTransition
from Engine.Scene import Scene,BaseScene
# from Scripts.ProgramManager import ProgramManager

from Utils.debug import Tracer
from Utils.events import EventChannel
from Utils.Time import Time
import Engine.Settings as Settings
  

class Engine:
    def __init__(self,resources_dir:str = '') -> None:
        # Currently the window does not exist

        # MGL context
        # self.ctx = mgl.create_context(standalone=True) #Headless Context

        # Time variables
        self.clock = Clock()
        self.time = Time()
        self.tracer = Tracer()


        self.event_channel = EventChannel()
        # Project handler
        # self.program_manager = ProgramManager(self.ctx)
        self.scenes:dict[str,BaseScene] = {
            # 'scene1': Scene(self)
        }
        self.active_scene:BaseScene
        self.next_scene:BaseScene|None = None
        self.resources_dir = resources_dir or 'Assets'

    ## Scene Management ##

    def SceneGet(self,name:str):
        return self.scenes[name]

    def SceneAdd(self,name:str,scene:BaseScene):
        if name in self.scenes: raise KeyError
        self.scenes[name] = scene

    def SceneDelete(self,name:str) -> BaseScene:
        '''Returns the deleted Scene'''
        return self.scenes.pop(name)
        
    def SceneLoad(self,name:str):
        if self.next_scene is not None: raise NotImplementedError
        self.next_scene =  self.SceneGet(name)

    ## End Scene Management ##

    def loadResources(self):
        pass
        
    ## Public Engine API ##


    def Start(self) -> bool: 
        '''
        Guaranteed to execute prior to Engine.Run (Only before, *not* RIGHT before)    
        The Window was just created. 
        Pygame is initialized.
        '''
        
        
        self.scenes['scene1'] = Scene(self)
        self.active_scene = self.scenes['scene1']
        return True
        
    def Run(self):
        '''
        Guaranteed to execute after Engine.Start . 
        Engine is fully initialized.
        '''
        running = True 
        self.time.start()
        self.active_scene.start()
        scene_trans:BaseTransition|None = None
        screen = pygame.display.get_surface()
        cleanup = False
        while running:
            '''
            Engine Takes Care of a few special events like:
            QUIT: Immediately quits out of the engine, skips all cleanup
            ENGINE: Engine related events, 
            '''
            pygame.event.pump() #Let pygame do its thing before the frame
            
            self.time.update()
            if scene_trans is not None:
                assert self.next_scene is not None
                done = scene_trans.Step(screen)
                if done:
                    self.active_scene = self.next_scene
                    self.active_scene.start()
                    scene_trans = None
            else:
                self.active_scene.update()
                self.active_scene.draw(screen)
            #load queued scene (if any)
            if self.next_scene and scene_trans is None:
                scene_trans = self.active_scene.stop()

            '''Handle Engine Events after the Scene'''                
            for event in pygame.event.get(eventtype=Settings.ENGINE,pump=False): #Catch any engine events that may have been posted during the frame
                if event.dict.get('close',False):
                    # assume that cleanup flag is set
                    cleanup:bool = event.cleanup
                    running = False
            display.flip()
            self.clock.tick(60)
        #Exited Main Loop

        if cleanup:
            self.active_scene.stop()
            for scene in self.scenes.values():
                scene.release()
        else:
            print("Engine Exited without cleanup.")
        if __debug__:
            self.tracer.show()

