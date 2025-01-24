import math
import pygame as pg
class BackgroundAnim:
    fps:int
    __slots__ = 'cycles','fps','tiles'
    def __init__(self,fps:int):
        self.cycles:list[list[pg.Surface]] = []
        self.fps = fps


    def addAnim(self,cycle:list[pg.Surface],fps:int):
        if self.fps%fps != 0: raise ValueError("Invalid FPS")
        if __debug__:
            if len(cycle) == 1 and fps != self.fps:
                print('[Warning] FPS for non-animating surface should match the Background\'s fps (e.g. {})'.format(self.fps))
            
        r = self.fps // fps
        a = [frame for frame in cycle for _ in range(r)]
        self.cycles.append(a)

    def addStill(self,surf:pg.Surface):
        self.cycles.append([surf])

    def build(self,flush=True):
        length = math.lcm(*map(len,self.cycles))
        if __debug__:
            a = []
            for cycle in self.cycles:
                b = cycle*(length//len(cycle))
                a.append(b)
        else:
            a = [cycle*(length//len(cycle)) for cycle in self.cycles]

        if flush:
            self.flush()
        tiles = list(zip(*a,strict=True))
        return TilesAnimator(tiles,self.fps)
        
    def flush(self):
        self.cycles.clear()



class TilesAnimator:
    __slots__ = 'tiles','fps','t'
    def __init__(self,tiles:list[list[pg.Surface]],fps:float) -> None:
        self.tiles = tiles
        self.fps = fps
        self.t = 0.0

    def get_tiles(self,dt:float):
        self.t += dt * self.fps
        return self.tiles[self.t.__trunc__()%len(self.tiles)]
    
#This probably needs a few unit tests for sanity's sake but im to lazy.