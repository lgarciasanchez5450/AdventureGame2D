import os
import pygame
import typing

from Utils.strutils import split

from Utils.debug import Tracer

Directory = dict[str,typing.Union['Directory',pygame.Surface]]

class UnknownResource:
    __slots__ = 'path',
    def __init__(self,path:str):
        self.path = path

class ResourceManager:
    def __init__(self,dir:str):
        self.dir = dir
        self.hooks = {'png':pygame.image.load,
                      'jpg':pygame.image.load,
                      'jpeg':pygame.image.load,
                      'bmp':pygame.image.load}
        
    def updateHooks(self,hooks:dict[str,typing.Callable]):
        self.hooks.update(hooks)

    def load(self,added_path:str = ''):
        self.textures = {}
        path = os.path.join(self.dir,added_path) if added_path else self.dir
        self.textures = self.loadDirectoryRecursive(path)
    
    def getTex(self,path:str|typing.Sequence[str]) -> pygame.Surface:
        if isinstance(path,str):
            path = split(path,{'/','\\'})
        curr = self.textures
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
        print("path:",path)
        curr = self.textures
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
    # @Tracer().trace
    def loadDirectoryRecursive(self,directory:str) -> Directory: 
        '''Recursively Load all files in a directory and all subdirectories as well'''
        out = {}
       
        # Tracer().addDebug(directory)
        for name in os.listdir(directory):
            path = os.path.join(directory,name)
            if os.path.isdir(path):
                out[name] = self.loadDirectoryRecursive(path)
            else:
                out[name] = self.hooks.get(getExtension(name),UnknownResource)(path)
        return out

    def release(self):
        self.textures.clear()

def getExtension(file:str):
    '''Returns the extension of a file given its name. If extension not found, will return full filename'''
    return file.rsplit('.',1)[-1] if '.' in file else file