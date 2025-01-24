import math
from Entities.Entity import Entity
from Lib.Utils.Serializable import Serializeable,pack,unpack,sint,dint


class BaseComponent(Serializeable,abstract=True):
    i = 0
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.i = BaseComponent.i + 1
        BaseComponent.i += 1
    __slots__ = 'entity'
    def __init__(self,entity:Entity):
        self.entity = entity



class Animation(BaseComponent):
    __slots__ = 't','fps','cycle'
    def __init__(self,entity:Entity,animation:list[int],fps:int):
        super().__init__(entity)
        self.t:float = 0
        entity.renderid = animation[0]
        self.fps = fps
        self.cycle = animation

    def serialize(self) -> bytes:
        return pack(sint(self.fps),*map(sint,self.cycle))
    
    @classmethod
    def deserialize(cls,b:bytes):
        a = object.__new__(Animation)
        fps,*cycle = map(dint,unpack(b))
        a.t = 0
        a.fps = fps
        a.cycle = cycle
        return a
    



class Attributes(BaseComponent):
    __slots__ = '_str','_int','_def','_spd'
    def __init__(self,entity:Entity):
        super().__init__(entity)
        self._str = 0
        self._int = 0
        self._def = 0
        self._spd = 0

    def getAttackDamage(self,raw_dmg:float) -> float:
        added = self._str + self._int/15
        mult = self._str/100 + 1
        return (raw_dmg+added) * mult
    
    def getDamageTaken(self,raw_dmg:float) -> float:
        sub = self._def/20 + self._str/50
        percent_reduction = (2/3.1415926535) * math.atan(self._def*(3.1415926535/2000))
        return (raw_dmg - sub) * (1 - percent_reduction)
    
    def getMaxSpeed(self,raw_speed:float) -> float: #blocks per second, we havta be carefull because this should feel good not just "be" good
        return raw_speed * math.log10(self._spd+10)
    
    def getMagicCapacity(self,raw_capacity:float) -> float:
        return raw_capacity + self._int 
    
    def getMagicAttackDamage(self,raw_dmg:float) -> float:
        added = self._int/10
        mult = (self._int//100 * 0.5) + 1
        return (raw_dmg + added) * mult

    def serialize(self) -> bytes:
        return pack(sint(self._str),sint(self._int),sint(self._def),sint(self._spd))

    @classmethod
    def deserialize(cls,b:bytes) -> 'Attributes':
        s,i,d,sp = unpack(b)
        a = object.__new__(Attributes)
        a._str = dint(s)
        a._int = dint(i)
        a._def = dint(d)
        a._spd = dint(sp)
        return a