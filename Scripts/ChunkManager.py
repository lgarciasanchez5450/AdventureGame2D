import typing
import glm
import moderngl as mgl
from Scripts.Chunk import Chunk
from Scripts.Entities.Entity import Entity
import numpy as np
if typing.TYPE_CHECKING:
    from Engine.Scene import Scene
from Utils.debug import profile
import pygame as pg
from Utils.Math.game_math import collide_chunks2d

from Scripts.TerrainGeneration import TerrainGenerator
from Scripts.ChunkSaver import ChunkSaver
SIMULATION_DISTANCE = 8 #this does not change at runtime
ChunkPos = tuple[int,int]
BLOCK_SIZE = 16
class ChunkManager:
    def __init__(self,scene:"Scene") -> None:

        self.render_distance = 4 #in chunks
        self.scene = scene

        self.chunks:dict[ChunkPos,Chunk] = {}
        self.simulation_chunks:set[ChunkPos] = set()
        self.render_chunks:set[ChunkPos] = set()
        self.chunk_surfs:dict[ChunkPos,pg.Surface] = {}
        self.chunk_dirty:set[ChunkPos] = set()
        
        self.terrain_gen = TerrainGenerator(self)    
        self.recalculateActiveChunks(*self.scene.camera.last) 
        self.viewport_size = glm.ivec2(800,600)

    def addEntity(self,entity:Entity):
        cpos = (entity.pos//Chunk.SIZE).to_tuple()
        if cpos not in self.chunks: raise RuntimeError()
        self.chunks[cpos].addEntity(entity)

    
    def update(self):
        #update chunks
        entities_moved:list[tuple[Entity,ChunkPos]] = []
        for cpos in self.simulation_chunks:
            self.chunks[cpos].update(entities_moved)
        for entity,chunk in entities_moved:
            if chunk in self.simulation_chunks:
                self.chunks[chunk].addEntity(entity)


        self.terrain_gen.update()

    def getRenderChunks(self) -> typing.Iterable[ChunkPos]:
        vpbs = glm.vec2(self.viewport_size) / BLOCK_SIZE
        topleft = self.scene.camera.position - vpbs / 2
        bottomright = topleft + vpbs
        return collide_chunks2d(topleft.x,topleft.y,bottomright.x,bottomright.y,Chunk.SIZE)

    def draw(self,surf:pg.Surface):


        pass
        # block_size = 16 #pixels per block
        # pixels_per_chunk = block_size * Chunk.SIZE #pixels per block * blocks per chunk
        # #draw floor, then draw entities and particles
        # camera_position = self.scene.camera.position
        # # camera_cpos = glm.ivec2(self.scene.camera.position//Chunk.SIZE).to_tuple()
        # final_drawlist = []
        # for cpos in self.render_chunks:
        #     if cpos in self.chunk_dirty:
        #         self.chunk_dirty.remove(cpos)
                        
        
        # camera_pixel_coords = glm.ivec2(glm.floor(camera_position * block_size))
      
        #     chunk_pixels_coords = glm.ivec2(cpos) * pixels_per_chunk
        #     screen_position = chunk_pixels_coords - camera_pixel_coords
        #     surf.blit(self.chunks[cpos].getSurf(),screen_position.to_tuple())
        # pass



    def unloadChunk(self,cpos:ChunkPos,group:set[ChunkPos]):
        return self.unloadChunks({cpos},group)
        
    def unloadChunks(self,chunks:set[ChunkPos],group:set[ChunkPos]):
        group.difference_update(chunks)

    def loadChunk(self,cpos:ChunkPos,group:set[ChunkPos]):
        return self.loadChunks({cpos},group)
      
    def loadChunks(self,chunks:set[ChunkPos],group:set[ChunkPos]):
        new_chunks = chunks.difference(group)
        for cpos in new_chunks:
            if cpos not in self.chunks:
                # if self.chunk_saver.haschunk(cpos):
                #     c = self.chunk_saver.getchunkasync(cpos)
                # else:
                c = Chunk(cpos)
                self.terrain_gen.queueChunk(c)
                self.chunks[cpos] = c
                # self.chunkmeshes[cpos] = ChunkMesh(self.ctx,self.scene.program,c)
        group.update(new_chunks)
    
    def recalculateActiveChunks(self,cx,cy):
        #get chunks that will be added
        new_render_chunks = getAround(cx,cy,self.render_distance)
        new_simulation_chunks = getAround(cx,cy,SIMULATION_DISTANCE)

        for cpos in new_render_chunks.union(new_simulation_chunks):
            if cpos not in self.chunks:
                self.chunks[cpos] = Chunk(cpos)
                self.terrain_gen.queueChunk(self.chunks[cpos])


        self.render_chunks = new_render_chunks
        self.simulation_chunks = new_simulation_chunks



from Utils.Math.Fast import cache

  
def getAround(x:int,y:int,dist:int):
    return {(dx+x,dy+y) for dx,dy in getDeltas(dist)}

def getAroundLOD(x:int,y:int,LOD:int):
    return {(dx+x,dy+y) for dx,dy in getDeltas(LOD)}


def getAroundSimulationDistance(x:int,y:int):
    return {(dx+x,dy+y) for dx,dy in getDeltas(SIMULATION_DISTANCE)}
@cache
def getDeltas(xyr:int):
    deltas:list[ChunkPos] = []
    sqr_xyr = xyr*xyr-0.1 # remove the annoying nub
    for dx in range(-xyr,xyr+1,1):
        for dy in range(-xyr,xyr+1,1):
                if dx*dx+dy*dy <= sqr_xyr:
                    deltas.append((dx,dy)) 
    return deltas