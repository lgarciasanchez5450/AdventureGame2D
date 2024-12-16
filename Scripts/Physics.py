import typing
from Utils.Math.Collider import Collider2D
from Scripts.Chunk import Chunk
from Utils.Math.game_math import *
from Entities.Entity import Entity




'''
BEWARE, the optimized and optimized functions actually have different behavior, 
it is like enabling fast_math in jit numba functions.
The relaxation of strict conditions enables the optimized functions 
to not consider some (important?) edge cases and thus, be faster.
'''


def collide_entity_x_unoptimized(entity:Entity,chunks:dict[tuple[int,int],Chunk]):
    '''Returns: 
        * Bool: Whether a hit occured or not'''
    hit = False
    for cpos in collide_chunks2d(entity.collider.x_negative,entity.collider.y_negative,entity.collider.x_positive,entity.collider.y_positive,Chunk.size):
        for block in chunks[cpos].blocks:
            if entity.collider.collide_collider(block.collider):
                if entity.vel.x > 0: # moving right
                    entity.collider.setXPositive(block.collider.x_negative)
                elif entity.vel.x < 0: 
                    entity.collider.setXNegative(block.collider.x_positive)
                entity.vel.x = 0
                hit = True
    return hit

def collide_entity_x_optimized(entity:Entity,chunks:dict[tuple[int,int],Chunk]):
    ec = entity.collider
    if entity.vel.x == 0: return False
    for cpos in collide_chunks2d(ec.x_negative,ec.y_negative,ec.x_positive,ec.y_positive,Chunk.size):
        for block in chunks[cpos].blocks:
            if ec.collide_collider(block.collider):
                if entity.vel.x > 0: # moving right
                    ec.setXPositive(block.collider.x_negative)
                else: 
                    ec.setXNegative(block.collider.x_positive)
                entity.vel.x = 0
                return True
    return False
               
def collide_entity_y_unoptimized(entity:Entity,chunks:dict[tuple[int,int],Chunk]) -> bool:
    '''Returns: 
        * Bool: Whether a hit occured or not'''
    hit = False
    for cpos in collide_chunks2d(entity.collider.x_negative,entity.collider.y_negative,entity.collider.x_positive,entity.collider.y_positive,Chunk.size):
        for block in chunks[cpos].blocks:
            if entity.collider.collide_collider(block.collider):
                if entity.vel.x > 0: # moving right
                    entity.collider.setXPositive(block.collider.x_negative)
                elif entity.vel.x < 0: 
                    entity.collider.setXNegative(block.collider.x_positive)
                entity.vel.x = 0
                hit = True
    return hit

def collide_entity_y_optimized(entity:Entity,chunks:dict[tuple[int,int],Chunk]):
    ec = entity.collider
    if entity.vel.y == 0: return False
    for cpos in collide_chunks2d(ec.x_negative,ec.y_negative,ec.x_positive,ec.y_positive,Chunk.size):
        for block in chunks[cpos].blocks:
            if ec.collide_collider(block.collider):
                if entity.vel.y > 0: # moving down
                    ec.setYPositive(block.collider.y_negative)
                else: 
                    ec.setYNegative(block.collider.y_positive)
                entity.vel.y = 0
                return True
    return False


class Physics2D:
    # '''
    # Creates a context of 2-dimensional Physics related functions.
    # Special Arguments:
    #     <o> : Optimization
    #         0 => No Optimization
    #         1 => Optimization Enabled
    # '''
    def __init__(self,worldManager):
        self.b_chunks = {}
        self.e_chunks:dict[tuple[int,int],list[Entity]] = {}
        self.big_entities:list[Entity] = []

    

    def collide_x(self,entity:Entity) -> bool: ...

    def collide_y(self,entity:Entity) -> bool: ...

    def getCollidingChunks(self,collider:Collider2D):
        return collide_chunks2d(collider.x_negative,collider.y_negative,collider.x_positive,collider.y_positive,Chunk.size)
    def getCollidingBlocks(self,collider:Collider2D):
        return collide_chunks2d(collider.x_negative,collider.y_negative,collider.x_positive,collider.y_positive,1)
    
    def getEntitiesCollidingRect(self,rect:Collider2D):
        for cpos in collide_chunks2d(rect.x_negative,rect.y_negative,rect.x_positive,rect.y_positive,Chunk.size):
            e_chunk = self.e_chunks.get(cpos)
            if e_chunk is not None:
                for entity in e_chunk:
                    if rect.collide_collider(entity.collider): pass

    