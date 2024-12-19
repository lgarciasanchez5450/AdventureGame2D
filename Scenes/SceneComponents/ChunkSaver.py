import typing
from Lib import Engine
import numpy as np
from Lib.Utils import lzip
from Entities.Entity import Entity
from Entities.Entity import Block
from Scripts.EntityComponents import BaseComponent
from Lib.Utils.Serializable import serialize,deserialize,pack,unpack
dtype_from_string = {
    'uint8': np.empty(1,np.uint8   ).dtype,
    'uint16':np.empty(1,np.uint16  ).dtype,
    'uint32':np.empty(1,np.uint32  ).dtype,
    'uint64':np.empty(1,np.uint64  ).dtype,
    'int8':  np.empty(1,np.int8    ).dtype,
    'int16': np.empty(1,np.int16   ).dtype,
    'int32': np.empty(1,np.int32   ).dtype,
    'int64': np.empty(1,np.int64   ).dtype,
    'float16':np.empty(1,np.float16).dtype,
    'float32':np.empty(1,np.float32).dtype,
    'float64':np.empty(1,np.float64).dtype,
}
string_from_dtype = {t:s for s,t in dtype_from_string.items()}
assert len(string_from_dtype)==len(dtype_from_string),'Bad!'

def loadChunk(path:str) -> bytes:
    with open(path,'rb') as file:
        return file.read()


class Chunk:
    @staticmethod
    def serialize(
        terrain:np.ndarray,
        blocks:list[Block],
        entities:dict[Entity,list[BaseComponent]],
    ) -> bytes:
        
        a = terrain.tobytes('C')
        b_ = [serialize(x) for x in blocks]
        c_ = [pack(serialize(c),*[serialize(comp) for comp in entities[c]]) for c in entities]
        sbytessize = 4
        header = f'dtype={string_from_dtype[terrain.dtype]},csize={terrain.shape[0]},blocks={len(b_)},entities={len(c_)},sbytessize={sbytessize}'.encode('ascii')
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
        return header + b':' + len(a).to_bytes(sbytessize,'big',signed=False)+a+b+c
    
    @staticmethod
    def deserialize(bin:bytes) -> tuple[np.ndarray,list[Block],dict[Entity,list[BaseComponent]]]:
        def p(b:str) -> list[str]:
            return b.split('=',1)
        header,data = bin.split(b':',1)
        headers = {k:v for k,v in map(p,header.decode('ascii').split(','))}
        dtype = dtype_from_string[headers['dtype']]
        sbytessize = int(headers['sbytessize'])
        num_entities = int(headers['entities'])
        csize = int(headers['csize'])

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

        terrain = np.frombuffer(terrain_,dtype).reshape((csize,csize))
        b:list[Block] = [deserialize(x) for x in b_] #type: ignore
        assert all(isinstance(x,Block) for x in b),b
        c:dict[Entity,list] = {}
        for by in c_:
            e,*comp = [deserialize(b) for b in unpack(by)] #type: ignore
            assert isinstance(e,Entity)
            assert all(isinstance(x,BaseComponent) for x in comp)
            comp:list[BaseComponent]
            for x in comp:
                x.entity = e #type: ignore
            c[e] = comp #type: ignore 
        return terrain,b,c

class ChunkSaver:
    def __init__(self,dirpath:str):
        self.resource_manager_t = Engine.ResourceManager(dirpath)
        self.resource_manager_t.load_hooks = {'chk':loadChunk}
        self.saved:set[tuple[int,int]] = set()
        for file in self.resource_manager_t.listDir('.'):
            if file.endswith('.chk'):
                x,y = file.removesuffix('.chk').split('-')
                self.saved.add((int(x),int(y)))

    def save(self,terrain:np.ndarray,blocks:list[Block],entities:dict[Entity,list[BaseComponent]],cpos:tuple[int,int]): 
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        serialized = Chunk.serialize(terrain,blocks,entities)
        print(serialized)
        compressed = lzip.compress(serialized)
        self.resource_manager_t.saveAsset(filename,compressed)
        self.saved.add(cpos)

    def load(self,cpos:tuple[int,int]):
        filename = f'{cpos[0]}-{cpos[1]}.chk'
        self.saved.remove(cpos)
        compressed:bytes = self.resource_manager_t.loadAsset(filename)
        print('compressed:',compressed)        
        serialized = lzip.decompress(compressed)
        terrain,blocks,entities = Chunk.deserialize(serialized)
        return terrain, blocks,entities

    def haschunk(self,cpos:tuple[int,int]):
        return cpos in self.saved

    def release(self):
        self.resource_manager_t.release()