import typing
import glm
import numpy as np
import numpy.typing as npt
from Scripts.Physics import Physics2D
from Scripts.Pipeline import Pipeline
from Scripts.ChunkSaver import ChunkSaver
from Utils.Math.Collider import Collider2D
from Utils.Math.game_math import collide_chunks2d as _collide
from Entities.Entity import Entity,Block


type CPOS = tuple[int,int] # Python 3.12 Specific Syntax
type POS = CPOS



class WorldManager:
    def __init__(self,chunk_size:int = 8):
        self.chunk_size = chunk_size 
        self.ebig_threshold = chunk_size//2
        #Data Holders
        self.active_chunks:set[CPOS] = set() 
        self.terrain_chunks:dict[CPOS,npt.NDArray[np.unsignedinteger[typing.Any]]] = {}
        self.entity_chunks:dict[CPOS,list[Entity]] = {}
        self.blocks:dict[POS,Block] = {}
        self.big_entities:list[Entity] = []
        #Dependencies
        self.c_saver = ChunkSaver('Temp')
        self.terrain_gen:Pipeline[CPOS,npt.NDArray[np.unsignedinteger[typing.Any]]] = MissingPipline(np.zeros((self.chunk_size,self.chunk_size),dtype=np.uint8),self.terrain_chunks.update)
        # self.physics = Physics2D()

    ### Configuration Functions ###
    def setTerrainGenerationPipeline(self,pipeline:Pipeline[CPOS,npt.NDArray[np.unsignedinteger[typing.Any]]]):
        pipeline.callback = self.terrain_chunks.update
        self.terrain_gen = pipeline


    ### Chunk Managment Functions ###
    def setActiveChunks(self,chunks:set[CPOS]):
        self.active_chunks = chunks

    def loadChunks(self,chunks:set[CPOS]):
        chunks = chunks.difference(self.terrain_chunks.keys())
        self.terrain_gen.addMuchWork(chunks)
    
    def unloadChunks(self,chunks:set[CPOS]):
        chunks = chunks.intersection(self.terrain_chunks.keys())
        for chunk in chunks:
            positions = [(x,y) for y in range(chunk[1]*self.chunk_size,(chunk[1]+1)*self.chunk_size) for x in range(chunk[0]*self.chunk_size,(chunk[0]+1)*self.chunk_size)]
            blocks:list[Block] = [self.blocks[pos] for pos in positions if pos in self.blocks]
            entities:list[Entity] = self.entity_chunks.get(chunk,[])
            if self.big_entities:
                for i in range(len(self.big_entities),-1,-1):
                    e = self.big_entities[i]
                    if glm.ivec2(e.position//self.chunk_size).to_tuple()==chunk:
                        entities.append(e)
                        self.big_entities.pop(i)
            terrain = self.terrain_chunks.pop(chunk)
            self.c_saver.save(terrain,blocks,entities,chunk)

    ### Spawning Functions ###
    def spawnEntity(self,entity:Entity):
        is_big = glm.any(entity.collider.s/2 >= glm.vec2(self.ebig_threshold)) #type: ignore
        if is_big:
            self.big_entities.append(entity)
            return True
        cpos = glm.ivec2(entity.position// self.chunk_size).to_tuple()
        if cpos in self.entity_chunks:
            self.entity_chunks[cpos].append(entity)
        else:
            self.entity_chunks[cpos] = [entity]
        return True

    def spawnBlock(self,block:Block):
        pos = glm.ivec2(glm.floor(block.position))
        assert self.blocks[pos.to_tuple()] is None, 'Undefined Behaviour for placing a 2 blocks in the same space'
        self.blocks[pos.to_tuple()] = block


    ### Collision Functions ###
    def iterEntitiesColliding(self,rect:Collider2D):
        og_size = rect.s
        rect.s = rect.s + self.ebig_threshold
        chunks = _collide(rect.x_negative,rect.y_negative,rect.x_positive,rect.y_positive,self.chunk_size)
        rect.s = og_size
        for cpos in chunks:
            chunk = self.entity_chunks.get(cpos)
            if chunk is not None:
                for entity in chunk:
                    if rect.collide_collider(entity.collider):
                        yield entity
        for entity in self.big_entities:
            if rect.collide_collider(entity.collider):
                yield entity

    def iterBlocksColliding(self,rect:Collider2D):
        og_size = rect.s
        rect.s = rect.s + self.ebig_threshold
        blocks = _collide(rect.x_negative,rect.y_negative,rect.x_positive,rect.y_positive,1)
        rect.s = og_size
        for pos in blocks:
            block = self.blocks.get(pos)
            if block is not None:
                if rect.collide_collider(block.collider):
                    yield block
        
    def release(self):
        self.c_saver.release()
    


class MissingPipline[K,V]:
    def __init__(self,retval:V,callback:typing.Callable[[typing.Mapping[K,V]],typing.Any]|None=None): 
        self.callback = callback or (lambda x: None)
        self.retval = retval
    def addMuchWork(self,work:typing.Iterable[K]): self.callback({k:self.retval for k in work})
    def addWork(self,one_work:K): self.callback({one_work:self.retval})
    def declareDependencies(self,key:K): pass
    def step(self,current:K) -> typing.Optional[V]: pass
    def updateDependencies(self): pass
    def update(self): pass
         
