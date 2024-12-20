import pygame
from pygame import display
from pygame.time import Clock
import pygame.constants as const

from .SceneTransitions.BaseTransition import BaseTransition
from .Scene import BaseScene
from .ResourceManager import ResourceManager
from . import Settings
from . import PreInitialization

from Lib.Utils.debug import Tracer #TODO find a way to get external dependencies to zero
from Lib.Utils.Time import Time 

class Engine:
    def __init__(self,resources_dir:str = '') -> None:
        # Currently the window does not exist

        # MGL context
        # self.ctx = mgl.create_context(standalone=True) #Headless Context

        # Time variables
        self.clock = Clock()
        self.time = Time()
        self.tracer = Tracer()
        self.target_fps = 60

        self.sceneCreator = lambda : {}


        # Project handler
        self.scenes:dict[str,BaseScene] = {}
        self.resource_manager = ResourceManager(resources_dir or 'Assets')
        self.active_scene:BaseScene
        self.next_scene:BaseScene|None = None

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


        
    ## Public Engine API ##
    def setFPS(self,fps:int):
        assert fps >= 0
        self.target_fps = fps

    def PreInit(self) -> bool:
        return PreInitialization.preinitialize()

    def Start(self) -> bool: 
        '''
        Guaranteed to execute prior to Engine.Run (Only before, *not* RIGHT before)    
        The Window was just created. 
        Pygame is initialized.
        '''
        if self.PreInit() is False:
            if __debug__:
                print("PreInitialization Failed!")
            return False

        self.resource_manager.load()
        self.scenes.update(self.sceneCreator())
        if len(self.scenes) == 0: 
            raise NotImplementedError("Undefined behaviour when no scenes implemented!")
        if not hasattr(self,'active_scene'):
            self.active_scene = self.scenes[list(self.scenes.keys())[0]]
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
            self.clock.tick(self.target_fps)
        #Exited Main Loop

        if cleanup:
            self.active_scene.stop()
            for scene in self.scenes.values():
                scene.release()
            self.resource_manager.release()
        else:
            print("Engine Exited without cleanup.")
        if __debug__:
            self.tracer.show()

