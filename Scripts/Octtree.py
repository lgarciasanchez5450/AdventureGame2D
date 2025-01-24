import typing
import glm



class ONode[T]:
    children:list['ONode']|None
    payload:list[T]|None
    def __init__(self) -> None:
        self.children = None
        self.payload = None
        
    def split(self):
        self.children = [ONode() for _ in range(8)]


class Octree2[K]:
    def __init__(self,position:tuple[int,int,int],size:int,max_depth:int=3) -> None:
        assert size.bit_count()==1,'<size> must be a power of 2!'
        self.root:ONode[K] = ONode()
        self.position = glm.ivec3(position)
        self.size:int = size
        self.max_depth= max_depth

    def insert(self,x:int,y:int,z:int,value:K):
        current = self.root
        ox,oy,oz = self.position
        size = self.size >> 1
        for _ in range(self.max_depth):
            x_ = x >= ox + size
            y_ = y >= oy + size
            z_ = z >= oy + size
            ox += x_ * size
            oy += y_ * size
            oz += z_ * size
            size >>= 1

            i = x_ + y_ * 2 + z_ * 4
            if current.children is None:
                current.children =  [ONode(), ONode(), ONode(), ONode(), ONode(), ONode(), ONode(), ONode()]
            current = current.children[i]

        if current.payload is None:
            current.payload = []
            
        current.payload.append(value)


class Quadtree[K]:
    def __init__(self,position:tuple[int,int],size:int,max_depth:int=3) -> None:
        assert size.bit_count()==1,'<size> must be a power of 2!'
        self.root:ONode[K] = ONode()
        self.position = glm.ivec2(position)
        self.size:int = size
        self.max_depth= max_depth

    def insert(self,x:int,y:int,value:K):
        current = self.root
        ox,oy,oz = self.position
        size = self.size >> 1
        for _ in range(self.max_depth):
            x_ = x >= ox + size
            y_ = y >= oy + size
            ox += x_ * size
            oy += y_ * size
            size >>= 1
            i = x_ + y_ * 2
            if current.children is None:
                current.children =  [ONode(), ONode(), ONode(), ONode()]
            current = current.children[i]

        if current.payload is None:
            current.payload = []

        current.payload.append(value)

    def get(self,x:int,y:int) -> typing.Optional[typing.Sequence[K]]:
        current = self.root
        ox,oy,oz = self.position
        size = self.size >> 1
        for _ in range(self.max_depth):
            x_ = x >= ox + size
            y_ = y >= oy + size
            ox += x_ * size
            oy += y_ * size
            size >>= 1
            i = x_ + y_ * 2
            if current.children is None:
                return None
            current = current.children[i]
        return current.payload