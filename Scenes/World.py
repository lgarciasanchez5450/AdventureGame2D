import typing
import Engine
import pygame
import glm
import numpy as np
from Engine.SceneTransitions.BaseTransition import BaseTransition
from Utils.debug import Tracer
from pygame import constants as const
from Entities.Entity import Entity, Block
from Scripts.Chunk import Chunk
from Scripts.ChunkSaver import ChunkSaver
from Scripts.TerrainGeneration import TerrainGen
from Scripts.WorldManager import WorldManager

class DrawComponent(typing.Protocol):
    position:glm.vec2
    renderid:int

class Layer:
    def __init__(self,max_drawables:int=-1):

        self.drawables:list[DrawComponent] = []
        self.max = max_drawables

    def addDrawable(self,drawcomp:DrawComponent):
        if len(self.drawables) == self.max: return False
        self.drawables.append(drawcomp)
        return True
    
    def removeDrawable(self,drawcomp:DrawComponent):
        if len(self.drawables) == 0: return False
        self.drawables.remove(drawcomp)
        return True
    
    def getDrawList(self,cam_pos:glm.vec2):
        for drawable in self.drawables:
            yield glm.floor((drawable.position - cam_pos) * 32),drawable.renderid

class LayerYSort(Layer):
    def getDrawList(self,cam_pos:glm.vec2):
        self.drawables.sort(key = lambda x:x.position.y)
        return super().getDrawList(cam_pos)

class World(Engine.BaseScene):
    def __init__(self,engine:Engine.Engine) -> None:
        self.engine = engine
        self.viewport_size = (800,500)
        self.world_surf = None

        self.invalid_chunk = np.zeros((8,8),dtype = np.uint8)
        
        self.world = WorldManager(8)        
        
        tiles = self.engine.resource_manager.getDir('NewTiles')
        null_tex = pygame.transform.scale(self.engine.resource_manager.getTex('Ground/null.png'),(32,32))
        self.layer_entities = LayerYSort()
        

        self.tiles = [null_tex]
        self.tiles.append(tiles['Water']['sprite_0.png']) #type: ignore
        self.tiles.append(tiles['Grass']['sprite_0.png']) #type: ignore
        self.tiles.extend(tiles['WaterBorderGrassBottom'].values()) #type: ignore
        self.tiles.extend(tiles['WaterBorderGrassTop'].values()) #type: ignore
        self.tiles = list(map(pygame.Surface.convert,self.tiles))

        self.player_pos = glm.vec2()
        self.camera_position = glm.vec2(self.player_pos)
        self.recalcChunks()

    def recalcChunks(self):
        c = glm.ivec2(self.player_pos//8)
        new = {(x,y) for x in range(c.x-3,c.x+4,1) for y in range(c.y-2,c.y+3,1)}
        
        # for cpos in new-self.active_chunks:#iterate over new chunks: (chunks that are in the new chunks but not the old ones)
        #     # load entities
            ### ^^ now taken care of in the draw function

        self.world.loadChunks(new)
        self.world.setActiveChunks(new)

     

    def start(self):
    #    self.layer_entities.addDrawable()
       print('Start called')

    def update(self):
        #process events
        dt = self.engine.time.dt
        for event in pygame.event.get(pump=False):
            if event.type == pygame.QUIT:
                pygame.event.post(Engine.Settings.ENGINE_CLOSE)
            elif event.type == pygame.WINDOWRESIZED:
                self.world_surf = None 

        
        #move character
        keys = pygame.key.get_pressed()

        w = keys[const.K_w]
        a = keys[const.K_a]
        s = keys[const.K_s]
        d = keys[const.K_d]
        vel = glm.vec2(d-a,s-w)
        starting_pos = self.player_pos//8
        self.player_pos += vel * 0.016666
        if self.player_pos//8 != starting_pos:
            self.recalcChunks()

        #move camera
        camera_adjust_rate = 0.1 #[0,1]
        self.camera_position += (self.player_pos - self.camera_position) * camera_adjust_rate

        #update order
        # we start with the invariant that all entities are alive 

        # 1)update all entities 
      
        # 2)move and collide entities
      
        # 3)do all damages, including explosions
        
      
        # 4)determine which entities are dead
        # 5)remove dead entities
        # we end with the invariant that all entities are alive 
        

        #update miscellaneous stuff
        

    def draw(self,screen:pygame.Surface):
        '''
        Optmized Drawing Routine for drawing and culling ground tiles
        '''
        if self.world_surf is None:
            self.world_surf = screen.subsurface((screen.get_width()-self.viewport_size[0])//2,(screen.get_height()-self.viewport_size[1])//2,self.viewport_size[0],self.viewport_size[1])
        # screen.fill('black')
        vw = self.viewport_size[0]
        vh = self.viewport_size[1]
        l:list[tuple[pygame.Surface,tuple[int,int]]] = []
        hx = vw//2
        hy = vh//2
        chunk_size = self.world.chunk_size
        for cpos in self.world.active_chunks:
            chunk = self.world.terrain_chunks.get(cpos,self.invalid_chunk)
            cx = cpos[0] * 8 - self.camera_position.x
            cy = cpos[1] * 8 - self.camera_position.y
            if cx < -32*chunk_size or cy < -32*chunk_size or cx >= vw or cy >= vh: continue
            for x in range(chunk_size):
                px = ((cx+x)*32).__floor__() + hx
                if px < -32 or px >= vw: continue
                for y in range(chunk_size):
                    py = ((cy+y)*32).__floor__() + hy
                    if -32 <= py < vh:
                        l.append((
                            self.tiles[chunk[x,y]],
                            (px,py)
                        ))
        self.world_surf.fblits(l)

        ## Start Unoptimized portion ##
        self.world_surf.fblits([(self.tiles[renderid],glm.ivec2(pos).to_tuple()) for pos,renderid in self.layer_entities.getDrawList(self.camera_position)])
            

    def stop(self):
        print('stop called')

    def release(self):
        self.world.release()
        print('release called')

