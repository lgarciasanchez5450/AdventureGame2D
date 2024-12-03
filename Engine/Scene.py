from Scripts.Player import Player
from Scripts.ChunkManager import ChunkManager
from Scripts.Physics import Physics
from Scripts.Camera import Camera2D
from Engine.SceneTransitions.BaseTransition import BaseTransition
import pygame
import numpy as np
import pygame as pg
import moderngl as mgl
from Utils.debug import Tracer
import glm
import typing
if typing.TYPE_CHECKING:
    from Engine.Engine import Engine
import Engine.Settings as Settings
from collections import deque

class BaseScene:
    def start(self): '''Called *right* before the first update'''
    def update(self): '''Called once every frame, before draw'''
    def draw(self,surf:pg.Surface): '''Called once every frame, after update'''
    def stop(self) -> BaseTransition: '''Once called, the next frame will not be this scene. Should *not* release all resources''';...
    def release(self): '''Called on Engine cleanup, *should* release all resources'''

import moderngl as mgl


class SampleScene(BaseScene):
    '''For all things diagetic (in game world/space)'''
    def __init__(self,engine:"Engine"):
        self.engine = engine

        self.fpsqueue = deque(maxlen=20)
        self.fps_sum = 0

    def update(self):

        # if pygame.event.get_grab():
        #     self.camera.update()
        #     self.camera.move()
        
        # self.chunk_manager.update()
        # self.physics.update()
        # mem_size = sys.getsizeof(self.chunk_manager.chunks)
        # mb = mem_size / 1_000_000
        # avg_chunk_size = mem_size//len(self.chunk_manager.chunks)
        fps = self.engine.time.getFPS()
        self.fpsqueue.append(fps)
        pygame.display.set_caption(f'{sum(self.fpsqueue) / len(self.fpsqueue):1f}')
        # mb = mem_footprint / 1_000_000
        # pygame.display.set_caption(f'{mb:.2f} MB')
        for event in pygame.event.get(pump=False):
            if event.type == pygame.constants.QUIT:
                pygame.event.post(Settings.ENGINE_CLOSE)


    def draw(self,surf:pg.Surface): ...
        # self.program['m_proj'].write(self.camera.m_projection) #type: ignore
        # self.program['m_view'].write(self.camera.m_view) #type: ignore
        # # self.ctx.clear(0.3,0.75,0.9)
        # self.ctx.clear(0.3,0.3,0.35)
        # surf.fill('blue')
        # self.program['m_model'].write(glm.translate(self.p)) #type: ignore
        # self.vao.render()
        # self.cube.render()
        # self.chunk_manager.draw()

        # self.ctx.screen.use()


@Tracer().trace
def tex_to_surf(texture:mgl.Texture,surf:pygame.Surface):
    bytes = texture.read()
    surf.get_view('2').write(bytes)


