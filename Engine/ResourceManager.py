import os
import pygame
import typing

Directory = dict[str,typing.Union['Directory',pygame.Surface]]

class ResourceManager:
    def __init__(self,dir:str):
        self.dir = dir

    def load(self,added_path:str = ''):
        self.textures = {}
        
        path = os.path.join(self.dir,added_path) if added_path else self.dir
        self.textures = self.loadDirectoryRecursive(path)
    

    def loadDirectoryRecursive(self,directory:str) -> Directory: 
        '''Recursively Load all files in a directory and all subdirectories as well'''
        return {name:pygame.image.load(os.path.join(directory,name)) if isTex(name) else self.loadDirectoryRecursive(os.path.join(directory,name)) for name in os.listdir(directory)}
            

def isTex(file:str):
    return file.rsplit('.',1)[-1] in {'png','jpg','jpeg','bmp'}