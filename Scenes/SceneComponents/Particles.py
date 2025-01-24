import typing
import glm
import numpy as np
import numpy.typing as npt

type RULE = typing.Literal['vectorized','per_particle']

class Particles:
    '''Class for basic, simple particles that are rendered with a simple shape like a circle'''
    def __init__(self):
        self._particles:dict[str,npt.NDArray] = {}
        self._plen:dict[str,int] = {}
        self._rules:dict[str,tuple[RULE,typing.Callable]] = {}

    def registerType(self,type:str,rule:RULE, func:typing.Callable,max_particles:int):
        self._rules[type] = (rule,func)
        self._particles[type] = np.empty((max_particles,2),dtype=np.float32)
        self._plen[type] = 0

    def spawnParticle(self,type:str,pos:tuple[float,float],size:int):
        pass


    def getParticlesByType(self,type:str):
        return self._particles[type]
        
    def getParticles(self) -> typing.Sequence[tuple[npt.NDArray[np.float32],np.uint16,str]]:...
