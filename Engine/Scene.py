from Scripts.Player import Player
from Scripts.ChunkManager import ChunkManager
from Scripts.Physics import Physics
from Scripts.Camera import Camera2D
from SceneTransitions.BaseTransition import BaseTransition
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


class Scene(BaseScene):
    '''For all things diagetic (in game world/space)'''
    def __init__(self,engine:"Engine"):
        self.engine = engine
    
        # self.camera = Camera2D(self,(1,5,1))
        # self.chunk_manager = ChunkManager(self)
        # self.physics = Physics(self)

        # surf_bottom = pygame.image.load('./Assets/Blocks/dirt.png').convert_alpha()
        # surf = pygame.image.load('./Assets/Blocks/grass_side.png').convert_alpha()
        # surf_top = pygame.image.load('./Assets/Blocks/grass_top.png').convert_alpha()
        
        # surf = pygame.transform.flip(surf,False,True)

        
        # self.tex = self.ctx.texture_array((surf.get_width(),surf.get_height(),3),4,
        #                         surf_top.get_view('1').raw +surf.get_view('1').raw+surf_bottom.get_view('1').raw
        #                        )
        # self.tex.swizzle = 'BGRA'
        # self.tex.anisotropy = 8
        # self.tex.build_mipmaps()
        # self.tex.filter = mgl.LINEAR_MIPMAP_LINEAR,mgl.NEAREST
        # self.program['tex'] = 3
        # self.tex.use(3)
        # self.program['textures'] = np.array([0,2,1,1,1,1],np.int32)
        # self.chunk_manager.addEntity(self.player)

        # self.cube = Cube((-1,-1,-1),self.program,self.ctx)
        # self.program['m_model'].write(glm.translate(position)) #type: ignore
        # self.program['m_proj'].write(self.camera.m_projection) #type: ignore
        # self.program['m_view'].write(self.camera.m_view) #type: ignore

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


