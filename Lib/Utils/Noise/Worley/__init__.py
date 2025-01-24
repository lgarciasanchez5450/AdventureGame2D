try:
    from numba import njit,prange
except ImportError:
    def njit(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper  
    prange = range

from math import floor,hypot, sqrt
import numpy
import random
try:
    from .internals import getAt,getArr,init
except:
    from internals import getAt,getArr,init

class WorleyNoise:
    '''Open World Noise (i.e. accepts any x and y to make noise)'''
    __slots__ = 'seed','_perm'
    def __init__(self,seed:int):
        self.seed = seed
        self._perm = init(seed)

    def getAt(self,x:float,y:float):
        return getAt(x,y,self._perm)

    def getArr(self,xs,ys):
        return getArr(xs,ys,self._perm)





if __name__ == "__main__":
    from time import perf_counter
    e = WorleyNoise(1)
    e.getArr(numpy.arange(10),numpy.arange(10))
    import pygame
    
    xs = numpy.arange(600)
    ys = numpy.arange(600)
    s = pygame.display.set_mode((600,600))
    SCALE = 0.6
    for y, row in enumerate(e.getArr(xs*SCALE,ys*SCALE)):
        for x, h in enumerate(row):
           
            s.set_at((x,y),(h*255,h*255,h*255))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
