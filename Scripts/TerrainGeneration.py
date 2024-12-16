import typing
import numpy as np
from collections import deque

from Scripts.Chunk import Chunk
from Scripts.Pipeline import PipelineLayer

from Utils.Noise.OpenSimplexLayered import LayeredOpenSimplex,OpenSimplex

def ret_and_clear(c):
    x = c.copy()
    c.clear()
    return x


overworld = {
    "height": LayeredOpenSimplex(0.006,3,2,0.5),
    # "temperature": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(10,o+10,1))),
    # "rainfall": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(20,o+20,1))),
}


    
class NewTerrainLayer(PipelineLayer[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]]):
    def step(self,cpos:tuple[int,int]):
        xs = np.arange(Chunk.size) + cpos[0] * Chunk.size
        ys = np.arange(Chunk.size) + cpos[1] * Chunk.size
        return xs,ys,overworld['height'].noise2array(xs,ys).T

class TerrainGen(PipelineLayer[tuple[int,int],Chunk]):
    @staticmethod
    def height_to_block(height:np.ndarray):
        # normalize to [0,1]
        height = (height + 1) / 2
        arr = np.empty_like(height,dtype=np.uint16)
        water_height = 0.5
        arr[height <water_height] = 1
        arr[np.logical_not(height <water_height)] = 2
        return arr
    
    def __init__(self,callback:typing.Callable[[typing.Mapping[tuple[int,int],Chunk]],typing.Any]):
        super().__init__(callback)
        self.dependency_terrain_input:dict[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]] = dict()
        self.dependency_terrain:NewTerrainLayer = NewTerrainLayer(self.dependency_terrain_input.update)
        self.current = None

    def declareDependencies(self, key: tuple[int, int]):
        self.dependency_terrain.addWork(key)

    def updateDependencies(self):
        self.dependency_terrain.update()

    def step(self,current:tuple[int,int]):
        terrain = self.dependency_terrain_input.get(current)
        #other dependencies go  here

        #make sure we have the dependencies we need for this chunk
        if terrain is not None:
            #safe to proceed
            xs,ys,height = terrain
            c = Chunk.noinit()
            c.array = self.height_to_block(height) #type: ignore
            return c




