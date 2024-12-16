import typing
import numpy as np
if typing.TYPE_CHECKING:
    from Entities.Entity import Entity
class Chunk:
    size:int = 8
    __slots__ = 'array','blocks'
    def __init__(self,dtype):
        self.array = np.empty((self.size,self.size),dtype=dtype)
        self.blocks:list[Entity] = []

    @classmethod
    def noinit(cls):
        return object.__new__(cls)