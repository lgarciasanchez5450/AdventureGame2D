import typing
import Engine
import numpy as np
from Utils import lzip
from Entities.Entity import Entity
from Entities.Entity import Block
       



dtype_from_string = {
    'uint8':np.uint8,
    'uint16':np.uint16,
    'uint32':np.uint32,
    'uint64':np.uint64,
    'int8':np.int8,
    'int16':np.int16,
    'int32':np.int32,
    'int64':np.int64,
    'float16':np.float16,
    'float32':np.float32,
    'float64':np.float64,
}
string_from_dtype = {t:s for s,t in dtype_from_string.items()}
assert len(string_from_dtype)==len(dtype_from_string)

class Chunk:
    @staticmethod
    def serialize(
        terrain:np.ndarray,
        blocks:list[Block],
        entities:list[Entity],
    ) -> bytes:
        
        a = terrain.tobytes('C')
        b_ = [Block.serialize(x) for x in blocks]
        c_ = [Entity.serialize(c) for c in entities]
        sbytessize = 4
        header = f'dtype={string_from_dtype[terrain.dtype]},blocks={len(b_)},entities={len(c_)},sbytessize={sbytessize}'.encode('ascii')
        b = bytearray()
        for sblock in b_:
            h = len(sblock).to_bytes(sbytessize,'big',signed=False)
            b.extend(h)
            b.extend(sblock)
        c = bytearray()
        for sentity in c_:
            h = len(sentity).to_bytes(sbytessize,'big',signed=False)
            c.extend(h)
            c.extend(sentity)
        return header + b'\n\r' + len(a).to_bytes(sbytessize,'big',signed=False)+a+b+c
    
    @staticmethod
    def deserialize(bin:bytes) -> tuple[np.ndarray,list[Block],list[Entity]]:
        def p(b:str) -> list[str]:
            return b.split('=',1)
        header,data = bin.split(b'\n\r',1)
        headers = {k:v for k,v in map(p,header.decode('ascii').split(','))}
        dtype = dtype_from_string[headers['dtype']]
        sbytessize = int(headers['sbytessize'])
        num_entities = int(headers['entities'])
        num_blocks= int(headers['blocks'])

        #split up the data
        #ORDER: terrain, blocks, entities
        size,data = int.from_bytes(data[:sbytessize],'big',signed=False),data[sbytessize:]
        terrain_,data = data[:size],data[size:]
        b_:list[bytes] = []
        for i in range(num_blocks):
            size,data = int.from_bytes(data[:sbytessize],'big',signed=False),data[sbytessize:]
            x,data = data[:size],data[size:]        
            b_.append(x)
        c_:list[bytes] = []
        for i in range(num_entities):
            size,data = int.from_bytes(data[:sbytessize],'big',signed=False),data[sbytessize:]
            x,data = data[:size],data[size:]        
            c_.append(x)

        terrain = np.frombuffer(terrain_,dtype)
        b = [Block.deserialize(x) for x in b_]
        c = [Entity.deserialize(x) for x in c_] 


        
        return terrain,b,c


def loadChunk(path:str) -> bytes:
    with open(path,'rb') as file:
        return file.read()


    
class ChunkSaver:
    def __init__(self,dirpath:str):
        self.resource_manager_t = Engine.ResourceManager(dirpath)
        self.resource_manager_t.load_hooks = {'chk':loadChunk}

        self.to_save:dict[tuple[int,int],Chunk] = {}
        self.saved:set[tuple[int,int]] = set()
        self.to_load:dict[tuple[int,int],Chunk] = {}
        
        for file in self.resource_manager_t.listDir('.'):
            if file.endswith('.chk'):
                x,y = file.removesuffix('.chk').split('-')
                self.saved.add((int(x),int(y)))

    def release(self):
        self.resource_manager_t.release()
        
    def step_load(self):
        cpos,chunk = self.to_load.popitem()
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        with self.resource_manager_t.loadAsset(filename,lambda path: open(path,'rb')) as file: ...
            # deserialize(lzip.decompress(file.read()),chunk)
# 
    def save(self,terrain:np.ndarray,blocks:list[Block],entities:list[Entity],cpos:tuple[int,int]): 
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        serialized = Chunk.serialize(terrain,blocks,entities)
        compressed = lzip.compress(serialized)
        self.resource_manager_t.saveAsset(filename,compressed)
        self.saved.add(cpos)

    def load(self,cpos:tuple[int,int]):
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        self.saved.remove(cpos)
        compressed:bytes = self.resource_manager_t.loadAsset(filename)
        serialized = lzip.decompress(compressed)
        terrain,blocks,entities = Chunk.deserialize(serialized)
        return terrain, blocks,entities
        


    def get(self,cpos:tuple[int,int]) -> 'Chunk': 
        chunk = self.to_save.pop(cpos,None)
        if chunk is not None:
            return chunk
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        return self.resource_manager_t.loadAsset(filename)
        
    def getAsync(self,cpos:tuple[int,int]) -> 'Chunk':
        chunk = self.to_save.pop(cpos,None)
        if chunk is not None:
            return chunk
        else:
            # c = Chunk(cpos)
            # self.to_load[cpos]=c
            return Chunk()
        
    def haschunk(self,cpos:tuple[int,int]):
        return cpos in self.saved or cpos in self.to_save


# def serialize(chunk:'Chunk') -> bytes:
#     b_ground = chunk.array.tobytes('C')
#     return b_ground

# def deserialize(b:bytes,chunk:typing.Optional['Chunk']=None) -> 'Chunk':
#     ground = np.frombuffer(b)
#     if chunk is None: chunk = Chunk.noinit()
#     chunk.array = ground
#     return chunk
