try:
    from Scripts import Biome, Block
    from Scripts.Chunk import Chunk #type: ignore
except: pass
import typing
from collections import deque
if typing.TYPE_CHECKING:
    from Scripts.ChunkManager import ChunkManager




class TerrainGenerator:
    MAX_CHUNKS_GEN_PER_FRAME = 150

    def __init__(self,chunkmanager:"ChunkManager"):
        self.chunk_manager = chunkmanager
        #                                                   nether   |  overworld
        self.dimension_heights = np.array([float('-inf'),-5000, -1000, -500, 1000,float('inf')],dtype=np.float32)
        self.queued:deque[Chunk] = deque()


    def queueChunk(self,chunk:Chunk):
        self.queued.append(chunk)


        
    def update(self) -> None:
        queue = self.queued
        i = 0
        while queue and i < self.MAX_CHUNKS_GEN_PER_FRAME:
            i+=1
            self.chunk_manager.dirty_chunks.add(generate(queue.popleft(),self.dimension_heights).pos)

from Utils.Noise.OpenSimplexLayered import LayeredOpenSimplex,OpenSimplex
overworld = {
    "height": LayeredOpenSimplex(0.01,6,2,0.5),
    "temperature": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(10,o+10,1))),
    "rainfall": LayeredOpenSimplex(0.01,3,2,0.5, lambda o : list(range(20,o+20,1))),
}
nether = {
    "terrain": OpenSimplex(3)
}

import numpy as np
# from Utils.Noise import perlin

from Scripts.Chunk import ChunkStatus
import math



def generate(chunk:Chunk,dim_heights:np.ndarray):
    chunk.status = ChunkStatus.GENERATING
    xs = np.arange(Chunk.SIZE,dtype=np.float64) + chunk.pos[0] * Chunk.SIZE
    ys = np.arange(Chunk.SIZE,dtype=np.float64) + chunk.pos[1] * Chunk.SIZE
    zs = np.arange(Chunk.SIZE,dtype=np.float64) + chunk.pos[2] * Chunk.SIZE

    y_avg = (chunk.pos[1] + 0.5) * Chunk.SIZE
    chunk.dimension = getChunkDimensionality(dim_heights,y_avg)
    dim = chunk.dimension
    if 0<=dim<1:
        chunk.biome[:] = Biome.IN_BETWEEN
        chunk.blocks = np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),np.uint16)

        chunk.blocks[:] = Block.STONE
    elif 1<=dim<2: #nether
        blocks = nether["terrain"].noise3array(zs*0.1,ys*0.1,xs*0.1) > 0
        chunk.blocks = np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),np.uint16)

        chunk.blocks[:] = Block.AIR
        chunk.blocks[blocks] = Block.NETHERSTONE
        chunk.biome[:] = Biome.NETHER_BIOME
    elif 2<= dim<3: #transition between nether and overworld
        noise = nether['terrain'].noise3array(xs,zs,ys)
        netherstone = (noise+1)/2 > (dim%1)
        holes = noise < (-(dim%1))
        
        chunk.biome[:] = Biome.IN_BETWEEN
        chunk.blocks = np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),np.uint16)
        chunk.blocks[netherstone] = Block.NETHERSTONE
        chunk.blocks[~netherstone] = Block.STONE
        chunk.blocks[holes] = Block.AIR     
    elif 3<=dim<4: #overworld
        height = overworld['height'].noise2array(xs,zs) * 10
        # temperature = overworld['temperature'].noise2array(xs,zs)
        # rainfall = overworld['rainfall'].noise2array(xs,zs) 
        chunk.biome[:] = Biome.PLAINS
        if np.max(height) < np.min(ys):
            chunk.blocks = None
        else:
            chunk.blocks = np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),np.uint16)
            broadcast_heightmap(height,ys,chunk.blocks)

    else:
        chunk.biome[:] = Biome.IN_BETWEEN
        chunk.blocks = None

    # chunk.blocks[:] = Block.AIR
    # chunk.blocks[:,0,:] = 1
    # chunk.blocks[0,1,0] = 1    
    # chunk.blocks[-1,1,-1] = 1    
    

    chunk.status = ChunkStatus.GENERATED
    return chunk

from numpy import typing as nptyping


def getChunkDimensionality(dim_heights:nptyping.NDArray[np.float32],y:float):
    for i in range(len(dim_heights)-1):
        if np.isinf(dim_heights[i]):
            #dim_heights[i] must be -inf
            if y < dim_heights[i+1]:
                dist_from_border:float = np.abs(y - dim_heights[i+1])
                decimal = dist_from_border / (dist_from_border + 100)
                return 1 - decimal
        elif np.isinf(dim_heights[i+1]):
            if y > dim_heights[i]:
                dist_from_border:float = np.abs(y - dim_heights[i])
                decimal = dist_from_border / (dist_from_border + 100)
                return i + decimal
        else:
            t:float = (y - dim_heights[i])/(dim_heights[i+1]-dim_heights[i])
            if 0<=t <=1:
                return i + t
    return -1

def broadcast_heightmap(heightmap:np.ndarray,ys:np.ndarray,out:np.ndarray):
    chunk_size = ys.size
    for y in range(chunk_size):
        out[:,y,:] = heightmap.T > ys[y]
