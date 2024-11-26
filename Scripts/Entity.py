import typing
import glm
from Utils.Math.Collider import Collider2D
if typing.TYPE_CHECKING:
    from Engine.Scene import Scene
class Entity:
    __slots__ = 'scene','pos','vel','collider','mass','dead','dir'
    def __init__(self,position:tuple[int,int],size:tuple[float,float]|glm.vec2) -> None:
        self.pos = glm.vec2(position)
        self.vel = glm.vec2(0,0)
        self.collider = Collider2D(self.pos,size)
        self.mass = 1 #kg
        self.dead = False
        
    def update(self): ...

    