import typing
import numpy as np
from collections import deque
from Lib.Utils.Pipeline import PipelineLayer

from Lib.Utils.Noise.OpenSimplexLayered import LayeredOpenSimplex,OpenSimplex

def ret_and_clear(c):
    x = c.copy()
    c.clear()
    return x


overworld = {
    "height": LayeredOpenSimplex(0.06,3,2,0.5),
    # "temperature": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(10,o+10,1))),
    # "rainfall": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(20,o+20,1))),
}

from Lib.Utils.debug import Tracer

    
class NewTerrainLayer(PipelineLayer[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]]):
    __slots__ = 'chunk_size'
    def __init__(self,chunk_size:int, callback: typing.Callable[[typing.Mapping[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]], typing.Any] | None = None):
        super().__init__(callback)
        self.chunk_size = chunk_size

    def step(self,cpos:tuple[int,int]):
        xs = np.arange(self.chunk_size) + cpos[0] * self.chunk_size
        ys = np.arange(self.chunk_size) + cpos[1] * self.chunk_size
        return xs,ys,overworld['height'].noise2array(xs,ys).T

class TerrainGen(PipelineLayer[tuple[int,int],np.ndarray]):
    @staticmethod
    def height_to_block(height:np.ndarray):
        # normalize to [0,1]
        height = (height + 1) / 2
        arr = np.empty_like(height,dtype=np.uint16)
        water_height = 0.5
        arr[height <water_height] = 1
        arr[np.logical_not(height <water_height)] = 2
        return arr
    
    def __init__(self,chunk_size:int,callback:typing.Callable[[typing.Mapping[tuple[int,int],np.ndarray]],typing.Any]|None=None):
        super().__init__(callback)
        self.chunk_size = chunk_size
        self.dependency_terrain_input:dict[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]] = dict()
        self.dependency_terrain:NewTerrainLayer = NewTerrainLayer(chunk_size,self.dependency_terrain_input.update)
        self.current = None

    def declareDependencies(self, key: tuple[int, int]):
        self.dependency_terrain.addWork(key)

    @Tracer().trace
    def updateDependencies(self):
        self.dependency_terrain.update()

    def step(self,current:tuple[int,int]):
        terrain = self.dependency_terrain_input.get(current)
        #other dependencies go  here

        #make sure we have the dependencies we need for this chunk
        if terrain is not None:
            #safe to proceed
            xs,ys,height = terrain
            return self.height_to_block(height)






