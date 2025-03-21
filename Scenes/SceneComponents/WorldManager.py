import typing
import glm
import numpy as np
import numpy.typing as npt
from Lib.Utils.Pipeline import Pipeline
from Lib.Utils.Pipeline import MissingPipline
from Lib.Utils.Math.Collider import Collider2D
from Lib.Utils.Math.game_math import collide_chunks2d as _collide
from Entities.Entity import Entity,Block
from Scenes.SceneComponents.Weather import Weather
from Scenes.SceneComponents.ChunkSaver import ChunkSaver
from Scenes.SceneComponents.Particles import Particles
from Scripts.EntityComponents import BaseComponent
from Scripts.GameSeed import GameSeed
from Scripts.WorldGenContext import WorldGenContext
from Lib.Utils.debug import Tracer
from Scenes.SceneComponents.TerrainGeneration import terrainType,humidityType,temperatureType
T = typing.TypeVar('T',bound=BaseComponent)

type CPOS = tuple[int,int] # Python >=3.12 Specific Syntax
type POS = CPOS

# class Wave:
#     center:POS
#     speed:float #blocks / s
#     t:float 
#     total_energy:float #Joules
#     release_radius:float #blocks, the radius that the energy is released from [ ]
#     release_time:float# seconds , time it takes for the energy to be fully released by the source

class WorldManager:
    def __init__(self,seed:GameSeed,chunk_size:int = 8,):
        self.chunk_size = chunk_size 
        self.ebig_threshold = chunk_size//2

        #Data Holders
        self.active_chunks:set[CPOS] = set() 
        self.terrain_chunks:dict[CPOS,npt.NDArray[np.unsignedinteger[typing.Any]]] = {}
        self.entity_chunks:dict[CPOS,list[Entity]] = {}
        self.blocks:dict[POS,Block] = {}
        self.big_entities:list[Entity] = []
        self.e_components:list[dict[int,BaseComponent]] = [{} for _ in range(BaseComponent.i)]

        #Settings
        self.time_scale:float = seed.time_scale

        #Async Queues
        self.to_save:set[CPOS] = set()
        self.to_load:set[CPOS] = set()

        #Dependencies
        self.c_saver = ChunkSaver('Temp')
        self.weather = Weather(seed)    
        # self.physics = Physics2D()
        self.game_seed = seed
        self.particles = Particles()
        self.terrain_gen:Pipeline[CPOS,tuple[terrainType,humidityType,temperatureType]] = MissingPipline((np.zeros((self.chunk_size,self.chunk_size),dtype=np.uint8),0.0,0.0),self.combined_callback )

    def combined_callback(self,d:typing.Mapping[CPOS,tuple[terrainType,humidityType,temperatureType]]):
        self.terrain_chunks.update({cpos:v[0] for cpos,v in d.items()})
        self.weather.humidity.update({cpos:v[1] for cpos,v in d.items()})
        self.weather.temperature.update({cpos:v[2] for cpos,v in d.items()})

    ### Configuration Functions ###
    def setTerrainGenerationPipeline(self,pipeline:Pipeline[CPOS,tuple[terrainType,humidityType,temperatureType]]):
        pipeline.callback = self.combined_callback
        self.terrain_gen = pipeline

    def getTerrainGenerationPipeline(self):
        return self.terrain_gen
    
    def setTimeScale(self,t:float):
        assert 0<=t
        self.time_scale = t
    
    def getTimeScale(self) -> float:
        return self.time_scale

    ### Chunk Managment Functions ###
    def setActiveChunks(self,chunks:set[CPOS]):
        self.active_chunks = chunks

    def loadChunks(self,chunks:set[CPOS]):
        self.to_save.difference_update(chunks) 
        chunks = chunks.difference(self.terrain_chunks.keys())
        #completely new chunks should be added to terrain_gen
        saved = chunks.intersection(self.c_saver.saved)
        self.to_load.update(saved)
        #previously unloaded chunks should be queued into the to_load queue
        chunks.difference_update(saved)
        self.terrain_gen.addMuchWork(chunks)
    
    def unloadChunks(self,chunks:set[CPOS]):
        self.to_load.difference_update(chunks)
        chunks = chunks.intersection(self.terrain_chunks.keys())
        self.to_save.update(chunks)
    
    ### Entity Component Functions ###
    def getComponent(self,entity:Entity,component:type[T]) -> T:
        return self.e_components[component.i][entity.uuid] #type: ignore
    
    def getTryComponent(self,entity:Entity,component:type[T]) -> typing.Optional[T]:
        return self.e_components[component.i].get(entity.uuid) #type: ignore
    
    def hasComponent(self,entity:Entity,component:type[T]) -> bool:
        return component in entity.components
    
    def setComponent(self,entity:Entity,component:BaseComponent):
        entity.components.add(type(component))
        self.e_components[component.i][entity.uuid] = component


    def iterComponents(self,component:type[T]) -> typing.Iterable[T]:
        return self.e_components[component.i].values() #type: ignore

    ### Spawning Functions ###
    def spawnEntity(self,entity:Entity):
        is_big = any(entity.collider.s/2 >= glm.vec2(self.ebig_threshold)) #type: ignore
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
        blocks = _collide(rect.x_negative,rect.y_negative,rect.x_positive,rect.y_positive,1)
        for pos in blocks:
            block = self.blocks.get(pos)
            if block is not None and rect.collide_collider(block.collider):
                yield block

    ### Engine Functions ###
    @Tracer().traceas('Manager Update')
    def update(self,udt:float):
        dt = udt * self.time_scale
        ### Three parts,
        # Updating Entities, TerrainGen&Weather, Update Load and Unloading

        # we start with the invariant that all entities are alive 
        echunks = [self.entity_chunks[cpos] for cpos in self.active_chunks if cpos in self.entity_chunks]
        # 1)update all entities 
        for chunk in echunks:
            for entity in chunk:
                entity.update()
        # 2)move and collide entities
        @Tracer().trace
        def physics():
            for chunk in echunks:
                for entity in chunk:
                    if entity.vel.x:
                        entity.collider.move_x(entity.vel.x * dt)
                        for block in self.iterBlocksColliding(entity.collider):
                            if entity.vel.x > 0:
                                entity.collider.setXPositive(block.collider.x_negative)
                            else:
                                entity.collider.setXNegative(block.collider.x_positive)
                            entity.vel.x = 0
                    if entity.vel.y:
                        entity.collider.move_y(entity.vel.y * dt)
                        for block in self.iterBlocksColliding(entity.collider):
                            if entity.vel.y > 0:
                                entity.collider.setXPositive(block.collider.y_negative)
                            else:
                                entity.collider.setYNegative(block.collider.y_positive)
                            entity.vel.y = 0
        physics()
        # 3) update explosions
        #TODO add explosions

        #remove dead entities, and move entities to their proper chunks
        dead_entities:list[Entity] = []
        moved_entities:list[tuple[Entity,CPOS]] = []
        for cpos in self.active_chunks:
            chunk = self.entity_chunks.get(cpos)
            if chunk is None: continue
            for i in range(len(chunk)-1,-1,-1):
                e = chunk[i]
                if e.dead:
                    dead_entities.append(chunk.pop(i))
                elif (n_cpos := glm.ivec2(e.position//self.chunk_size).to_tuple()) != cpos:
                    moved_entities.append((chunk.pop(i),n_cpos))
        for e,cpos in moved_entities:
            if cpos in self.entity_chunks:
                self.entity_chunks[cpos].append(entity)
            else:
                self.entity_chunks[cpos] = [entity]
        for d_entity in dead_entities:
            # remove their components
            for comp in d_entity.components:
                del self.e_components[comp.i][d_entity.uuid]
            del d_entity.components
            print(f"Entity {d_entity} died.")
        # we end with the invariant that all entities are alive 
        
        self.terrain_gen.update()
        self.weather.update(dt)
        

        to_unload = min(len(self.to_save),2)
        while to_unload:
            self.unloadChunkAtomic(self.to_save.pop())
            to_unload -=1

        to_load = min(len(self.to_load),2)
        while to_load:
            self.loadChunkAtomic(self.to_load.pop())
            to_load -=1

    def unloadChunkAtomic(self,cpos:CPOS):
        positions = [(x,y) for y in range(cpos[1]*self.chunk_size,(cpos[1]+1)*self.chunk_size) for x in range(cpos[0]*self.chunk_size,(cpos[0]+1)*self.chunk_size)]
        blocks:list[Block] = [self.blocks.pop(pos) for pos in positions if pos in self.blocks]
        entities:list[Entity] = self.entity_chunks.pop(cpos,[])
        if self.big_entities:
            for i in range(len(self.big_entities),-1,-1):
                e = self.big_entities[i]
                if glm.ivec2(e.position//self.chunk_size).to_tuple()==cpos:
                    entities.append(e)
                    self.big_entities.pop(i)
        terrain = self.terrain_chunks.pop(cpos)                    
        self.c_saver.save(terrain,blocks,{entity:[self.e_components[comp.i].pop(entity.uuid) for comp in entity.components] for entity in entities},cpos)

    def loadChunkAtomic(self,cpos:CPOS):
        terrain,blocks,entities = self.c_saver.load(cpos)
        self.terrain_chunks[cpos] = terrain
        for block in blocks:
            self.spawnBlock(block)
        if cpos not in self.entity_chunks:
            e = self.entity_chunks[cpos] = []
        else:
            e = self.entity_chunks[cpos]
        for entity in entities:
            if any(entity.collider.s/2 >= glm.vec2(self.ebig_threshold)): #type: ignore
                self.big_entities.append(entity)
            else:
                e.append(entity)
            for comp in entities[entity]:
                self.setComponent(entity,comp)     

    ### Misc Functions ###     
    def release(self):
        self.c_saver.release()
    
