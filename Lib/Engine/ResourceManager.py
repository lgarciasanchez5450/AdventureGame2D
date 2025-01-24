import os
import pygame
import typing

from Lib.Utils.strutils import split

from Lib.Utils.debug import Tracer

Directory = dict[str,typing.Union['Directory',pygame.Surface]]
T = typing.TypeVar('T')

class UnknownResource:
    __slots__ = 'path',
    def __init__(self,path:str):
        self.path = path

def default_save(path:str,resource:typing.Any):
    if isinstance(resource,(bytes,bytearray)):
        b = resource
    else:
        b = str(resource).encode()
    with open(path,'wb+') as file:
        file.write(b)




class ResourceManager:
    ### You know i thought this(having a resource manager) would be a really good idea, but the more I use it the more i realize
    # that I have to go out of my way to use it and it can be pretty cumbersome to jump through hoops to get any benefits from it.
    # maybe a rewrite is needed or just strip this out.
    '''
    Method Prefixes:
     * get -> retrieves from preloaded assets
     * load -> loads new asset from file


    '''
    def __init__(self,dir:str):
        os.makedirs(dir,exist_ok=True)
        self.dir = dir
        self.load_hooks:dict[str,typing.Callable[[str],typing.Any]] = {'png':pygame.image.load,
                                                'jpg':pygame.image.load,
                                                'jpeg':pygame.image.load,
                                                'bmp':pygame.image.load}
        self.save_hooks:dict[type,typing.Callable[[str,typing.Any],typing.Any]] = {}
        
        
    def updateHooks(self,hooks:dict[str,typing.Callable]):
        self.load_hooks.update(hooks)
    @Tracer().traceas('ResourceManager Load')
    def load(self,added_path:str = ''):
        self.assets = {}
        path = os.path.join(self.dir,added_path) if added_path else self.dir
        self.assets = self.loadDirectoryRecursive(path)
    
    def getTex(self,path:str|typing.Sequence[str]) -> pygame.Surface:
        path = splitPath(path)
        curr = self.assets
        if __debug__:
            for key in path:
                if not isinstance(curr,(typing.Sequence,dict)):
                    raise ValueError(f'Invalid Texture Path: {'/'.join(path)} \nError at: {key}')
                else:
                    curr = curr[key] #type: ignore
            if isinstance(curr,dict): 
                raise ValueError(f'Invalide Texture Path: {'/'.join(path)}\nEnd Key was not surface!')
            return curr
        else:
            for key in path:
                curr = curr[key] #type: ignore
            return curr #type: ignore

    def getDir(self,path:str|typing.Sequence[str]) -> Directory:
        if isinstance(path,str):
            path = split(path,{'/','\\'})
        curr = self.assets
        if __debug__:
            for key in path:
                if not isinstance(curr,(typing.Sequence,dict)):
                    raise ValueError(f'Invalid Texture Path: {'/'.join(path)} \nError at: {key}')
                else:
                    curr = curr[key] #type: ignore
            if not isinstance(curr,dict): 
                raise ValueError(f'Invalide Texture Path: {'/'.join(path)}\nEnd Key was not Directory!')
            return curr
        else:
            for key in path:
                curr = curr[key] #type: ignore
            return curr #type: ignore

    def loadDirectoryRecursive(self,directory:str) -> Directory: 
        '''Recursively Load all files in a directory and all subdirectories as well'''
        out = {}       
        for name in os.listdir(directory):
            path = os.path.join(directory,name)
            if os.path.isdir(path):
                out[name] = self.loadDirectoryRecursive(path)
            else:
                out[name] = self.load_hooks.get(getExtension(name),UnknownResource)(path)
        return out

    def loadAsset(self,path:str|typing.Sequence[str],resourceType:typing.Callable[[str],T]|None=None) -> T:
        '''Not collected when Resource Manager is released'''
        path = self.absPath(path)
        name = splitPath(path)[-1]
        return (resourceType or self.load_hooks.get(getExtension(name),UnknownResource))(path)
    
    def loadAssetStrict(self,path:str|typing.Sequence[str],resourceType:typing.Callable[[str],T]) -> T:
        '''Not collected when Resource Manager is released'''
        path = self.absPath(path)
        name = splitPath(path)[-1]
        return (resourceType or self.load_hooks.get(getExtension(name),UnknownResource))(path)

    def saveAsset(self,path:str|typing.Sequence[str],resource,ensure_path:bool=False):
        if ensure_path:
            os.makedirs(self.absPath(splitPath(path)[:-1]),exist_ok=True)
        abs_path= self.absPath(path)

        self.save_hooks.get(type(resource),default_save)(abs_path,resource)

        # path = splitPath(path)
        # cur = self.assets
        # for key in path[:-1]:
        #     if key not in cur:
        #         cur[key] = {}
        #     cur = cur[key]
        #     if not isinstance(cur,(dict,typing.Mapping)):
        #         raise ValueError(f'Invalide Texture Path: {'/'.join(path)}\nEnd Key was not Directory!')
        # cur[path[-1]] = resource    #type: ignore 

    def listDir(self,path:str|typing.Sequence[str]):
        path = self.absPath(path)
        return os.listdir(path)
            
    def absPath(self,path:str|typing.Sequence[str]):
        return os.path.join(self.dir,*splitPath(path))

    def release(self,d:typing.Iterable|None=None):
        if d is None:
            if not hasattr(self,'assets'):
                return
            d = self.assets.values()
            clear = True
        else:
            clear = False

        for val in d:
            if isinstance(val,(dict,typing.Mapping)):
                self.release(val.values())
            elif isinstance(val,typing.Iterable):
                self.release(val)
            else:
                if hasattr(val.__class__,'release'):
                    val.__class__.release(val)
                elif hasattr(val.__class__,'close'):
                    val.__class__.close(val)
        if clear:
            self.assets.clear()

def getExtension(file:str):
    '''Returns the extension of a file given its name. If extension not found, will return full filename'''
    return file.rsplit('.',1)[-1] if '.' in file else file

def splitPath(s:str|typing.Sequence[str]) -> typing.Sequence[str]:
    if isinstance(s,str):
        return split(s,{'/','\\'})
    return s