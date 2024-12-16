import typing
import glm
from Utils.Math.Collider import Collider2D
esubs:dict[str,type['Entity']] = {}
class Entity:
    def __init_subclass__(cls) -> None: 
        if cls.__name__ in bsubs: raise RuntimeError("No two subclasses may have the same name!")
        esubs[cls.__name__] = cls
        
    __slots__ = 'renderid','position','vel','collider','mass','dead'
    def __init__(self,position:tuple[float,float],size:tuple[float,float]|glm.vec2,renderid:int=0) -> None:
        self.renderid:int = renderid
        self.position = glm.vec2(position)
        self.vel = glm.vec2()
        self.collider = Collider2D(self.position,size)
        self.mass = 1 #kg
        self.dead = False
        
    def update(self): ...

    def takeDamage(self,dmg:float): ...

    def serialize(self) -> bytes: 
        return (self.__class__.__name__+":").encode('ascii') + self.__class__.serialize(self)

    @staticmethod
    def deserialize(b:bytes) -> 'Entity': 
        type,data = b.split(b':',1)
        return esubs[type.decode('ascii')].deserialize(data)



bsubs:dict[str,type['Block']] = {}
class Block:
    size:tuple[float,float] = (1,1)
    offset:tuple[float,float] = (0,0)

    def __init_subclass__(cls) -> None: 
        if cls.__name__ in bsubs: raise RuntimeError("No two subclasses may have the same name!")
        bsubs[cls.__name__] = cls
        
    __slots__ = 'position','collider','dead','renderid'
    def __init__(self,position:tuple[int,int],renderid:int=0):
        assert -1<=(self.offset[0] + self.size[1]) <= 1 and -1<=(self.offset[0] + self.size[1]) <= 1, 'Block must remain completely inside box'
        self.renderid:int = renderid
        self.position = glm.ivec2(position)
        self.collider = Collider2D(glm.vec2(self.position)+0.5 + self.offset,self.size)
        self.dead = False

    def serialize(block) -> bytes: #type: ignore
        return (block.__class__.__name__+":").encode('ascii') + block.__class__.serialize(block)
    
    @staticmethod
    def deserialize(b:bytes) -> 'Block': 
        type,data = b.split(b':',1)
        return bsubs[type.decode('ascii')].deserialize(data)

