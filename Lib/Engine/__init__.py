import sys
from .Engine import Engine
from .ResourceManager import ResourceManager
from .Scene import BaseScene
from . import Settings
import pygame as pg
from pygame import constants as const
from . import PreInitialization

__all__ = [
    'Engine',
    'ResourceManager',
    'PreInitialization',
    'BaseScene',
    'Settings',
    'pg',
    'const',
    'IgnoreScreenScaling'
]



if sys.platform == 'win32':
    def IgnoreScreenScaling():
        '''
        Signals to the operating system (i.e. Windows) to ignore any screen scaling set in system settings and let 
        this application have pixel-by-pixel control. This function's effects will continue until the application 
        closes. There is no way to get screen scaling back once this function is called for the remaining lifetime of
        the process.
        '''
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
else:
    def IgnoreScreenScaling():
        print(f'[Warning] Method <Engine.IgnoreScreenScaling> is unsupported on the current platform ({sys.platform})')
