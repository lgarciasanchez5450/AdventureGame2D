import typing
import glm
from Lib.Utils.Math.Collider import Collider2D
from Lib.Utils.Serializable import Serializeable,pack,unpack

if typing.TYPE_CHECKING:
    from Scripts.EntityComponents import BaseComponent

esubs:dict[str,type['Entity']] = {}
class Entity(Serializeable):
    __slots__ = 'renderid','position','vel','collider','mass','dead','components'
    def __init__(self,position:tuple[float,float]|glm.vec2,size:tuple[float,float]|glm.vec2,renderid:int=0) -> None:
        self.renderid:int = renderid
        self.position = glm.vec2(position)
        self.vel = glm.vec2()
        self.collider = Collider2D(self.position,size)
        self.mass = 1 #kg
        self.dead = False
        self.components:set[type[BaseComponent]] = set()
        
    def update(self): ...

    def takeDamage(self,dmg:float): ...

    @property
    def uuid(self):
        '''
        Returns a UUID that is valid for the entire lifespan of this entity object.
        Valid: 
         >>> entity1.uuid == entity2.uuid and entity1 is not entity2 # This statement will always be false
         False
         >>> id1 = entity1.uuid
         >>> del entity1
         >>> new_entity = Entity()
         >>> new_entity.uuid == id1 # This is undefined, as id1 is no longer a valid id since its entity no longer exists
        '''
        return id(self) 
    def __repr__(self):
        return f'Entity(pos={self.position.to_tuple()},vel={self.vel.to_tuple()},size={self.collider.size},mass={self.mass},renderid={self.renderid})'
    
    def serialize(self):
        return pack(self.position.to_bytes(),self.vel.to_bytes(),self.collider.s.to_bytes(),self.renderid.to_bytes(3,'big'),str(self.mass).encode())
    

    @classmethod
    def deserialize(cls,b:bytes):
        if isinstance(b,bytearray):
            b = bytes(b)
        p,v,s,rid,m = unpack(b)
        pos = glm.vec2.from_bytes(p)
        vel = glm.vec2.from_bytes(v)
        size = glm.vec2.from_bytes(s)
        renderid = int.from_bytes(rid,'big')
        mass = float(m.decode())
        e= Entity(pos,size,renderid)
        e.vel = vel
        e.mass = mass
        return e

class Block(Serializeable):
    size:tuple[float,float] = (1,1)
    offset:tuple[float,float] = (0,0)
    __slots__ = 'position','collider','dead','renderid'
    def __init__(self,position:tuple[int,int],renderid:int=0):
        assert -1<=(self.offset[0] + self.size[1]) <= 1 and -1<=(self.offset[0] + self.size[1]) <= 1, 'Block must remain completely inside box'
        self.renderid:int = renderid
        self.position = glm.ivec2(position)
        self.collider = Collider2D(glm.vec2(self.position)+0.5 + self.offset,self.size)
        self.dead = False

    @property
    def uuid(self):
        '''
        Returns a UUID that is valid for the entire lifespan of this entity object.
        Valid: 
         >>> block1.uuid == entity2.uuid and block1 is not entity2 # This statement will always be false
         False
         >>> id1 = block1.uuid
         >>> del block1
         >>> new_block = Block()
         >>> new_block.uuid == id1 # This is undefined, as id1 is no longer a valid id since its entity no longer exists
        '''
        return id(self) 
    
    def serialize(self):
        return pack(self.position.to_bytes(),self.renderid.to_bytes(3,'big'))

    @classmethod
    def deserialize(cls,b:bytes):
        p,rid = unpack(b)
        pos = glm.ivec2.from_bytes(p)
        renderid = int.from_bytes(rid,'big')
        bl= Block(pos.to_tuple(),renderid)
        return bl