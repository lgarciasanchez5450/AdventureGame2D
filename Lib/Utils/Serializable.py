import typing
T = typing.TypeVar('T')
abstracts:set[type['Serializeable']] = set()

def build_path(ancestor_class:type,current_path:str,paths:dict[type,str]):
    subclasses = ancestor_class.__subclasses__()
    #check for same names in subclasses
    assert len(subclasses) == len(set(x.__name__ for x in subclasses)), f'Subclasses cannot have the same names {subclasses}'
    for sub in subclasses:
        path = current_path + '/' + sub.__name__
        if (sub not in abstracts) and  (sub not in paths or len(path) < len(paths[sub])):
            paths[sub] = path
        build_path(sub,path,paths)
paths:dict[type['Serializeable'],str] = {}
types:dict[str,type['Serializeable']] = {}

class Serializeable:
    __slots__ = ()
    def __init_subclass__(cls,**kwargs) -> None:
        if kwargs.get('abstract') is True: 
            abstracts.add(cls)
        if __debug__: init()


    def serialize(self) -> bytes: ...
    @classmethod
    def deserialize(cls:typing.Callable[...,T],b:bytes) -> T: ...



def init():
    paths.clear()
    build_path(Serializeable,'',paths)
    types.clear()
    types.update({v:k for k,v in paths.items()})
if __debug__:
    from Lib.Utils.debug import profile
    init= profile(init)

    



def serialize(obj:Serializeable):
    prefix = paths[type(obj)]
    serialized = obj.serialize()
    return prefix.encode('ascii') + b':' + serialized

def deserialize(b:bytes) -> Serializeable:
    prefix,serialized = b.split(b':',1)
    class_ = types[prefix.decode('ascii')] 
    return class_.deserialize(serialized)
    



def pack(*a:bytes) -> bytearray:
    max_size = max(map(len,a))
    bits = max_size.bit_length()
    prefix_size = bits//8 + 1
    out = bytearray()
    out.append(prefix_size-1)
    for element in a:
        size = len(element)
        out.extend(size.to_bytes(prefix_size,'big',signed=False))
        out.extend(element)
    return out

def unpack(t:bytes|bytearray) -> list[bytes]:
    header = t[0]
    prefix_size = (header&0b11) + 1

    out:list[bytes] = []
    i = 1
    while i < len(t):
        l = int.from_bytes(t[i:i+prefix_size],'big',signed=False)
        i += prefix_size
        out.append(t[i:i+l])
        i+= l

    return out


def sint(i:int) -> bytes:
    return i.to_bytes(i.bit_length()//8 + 1,'big',signed=True)
def dint(b:bytes) -> int:
    return int.from_bytes(b,'big',signed=True)

def suint(i:int) -> bytes:
    return i.to_bytes(i.bit_length()//8 + 1,'big',signed=False)
def duint(b:bytes) -> int:
    return int.from_bytes(b,'big',signed=False)