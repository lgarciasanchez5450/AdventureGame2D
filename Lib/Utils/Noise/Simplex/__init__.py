# This file has been copied (and modified) from the opensimplex module installable by "pip install opensimplex"

from .constants import np
from .internals import _init, _noise2, _noise3, _noise4, _noise2a, _noise3a, _noise4a,_noise2a_ip, _noise3a_ip, _noise4a_ip
__all__ = [
    'OpenSimplex',
    'OpenSimplexLayered'
]

class OpenSimplex:
    __slots__ = '_perm','_perm_grad_index3','_seed'
    def __init__(self, seed: int) -> None:
        self.reseed(seed)

    def get_seed(self) -> int:
        return self._seed
    
    def reseed(self,seed:int):
        self._perm, self._perm_grad_index3 = _init(seed)
        self._seed = seed
        
    def noise2(self, x: float, y: float) -> float:
        return _noise2(x, y, self._perm)

    def noise2array(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return _noise2a(x, y, self._perm)

    def noise3(self, x: float, y: float, z: float) -> float:
        return _noise3(x, y, z, self._perm, self._perm_grad_index3)

    def noise3array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        return _noise3a(x, y, z, self._perm, self._perm_grad_index3)

    def noise4(self, x: float, y: float, z: float, w: float) -> float:
        return _noise4(x, y, z, w, self._perm)

    def noise4array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, w: np.ndarray) -> np.ndarray:
        return _noise4a(x, y, z, w, self._perm)



class OpenSimplexLayered(OpenSimplex):
    __slots__ = 'octaves','lacunarity','persistence','_squish_factor'
    def __init__(self,seed:int,octaves:int,lacunarity:float = 2.0,persistence:float = 0.5):
        super().__init__(seed)
        self.octaves = octaves
        self.lacunarity = lacunarity
        self.persistence = persistence
        #sum of the geometric series with a = 1 and r = persistence
        #we calculate the inverse so that we can multiply it with the arrays and save ourselves the headache of a possible DivBy0Error
        self._squish_factor = (1-persistence**octaves)/(1-persistence)
        if self._squish_factor != 0:
            self._squish_factor = 1.0 / self._squish_factor
        else:
            #here we would set the squich factor to 0 but that should already be the case
            pass

    def noise2(self, x: float, y: float) -> float:
        out = 0
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            out += _noise2(x * freq, y * freq,self._perm) * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor
        return out

    def noise2array(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        out = np.zeros((y.size, x.size), dtype=np.double)
        temp = np.empty((y.size, x.size), dtype=np.double)
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            _noise2a_ip(x * freq, y * freq, self._perm, temp)
            out += temp * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor
        return out

    def noise3(self, x: float, y: float, z: float) -> float:
        out = 0
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            out += _noise3(x * freq, y * freq, z * freq,self._perm, self._perm_grad_index3) * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor

        return out
    
    def noise3array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        out = np.zeros((z.size, y.size, x.size), dtype=np.double)
        temp = np.empty((z.size, y.size, x.size), dtype=np.double) # keep a np array to reuse between layers
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            _noise3a_ip(x * freq, y * freq, z * freq, self._perm, self._perm_grad_index3, temp)
            out += temp * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor

        return out

    def noise4(self, x: float, y: float, z: float, w: float) -> float:
        out = 0
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            out += _noise4(x * freq, y * freq, z * freq, w * freq, self._perm) * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor

        return out
    
    def noise4array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, w: np.ndarray) -> np.ndarray:
        out = np.zeros((w.size, z.size, y.size, x.size), dtype=np.double)
        temp = np.empty((w.size, z.size, y.size, x.size), dtype=np.double) # keep a np array to reuse between layers
        freq = 1
        amp = 1
        for _ in range(self.octaves):
            _noise4a_ip(x * freq, y * freq, z * freq, w * freq, self._perm, temp)
            out += temp * amp
            freq *= self.lacunarity
            amp *= self.persistence
        out *= self._squish_factor
        return out


def preinitialize(size:int=8):
    s = np.arange(size)*0.1
    perm,perm3d = _init(0)
    _noise2(s[0],s[0],perm)
    t = _noise2a(s,s,perm)
    _noise2a_ip(s,s,perm,t)
    _noise3(s[0],s[0],s[0],perm,perm3d)
    t = _noise3a(s,s,s,perm,perm3d)
    _noise3a_ip(s,s,s,perm,perm3d,t)
    _noise4(s[0],s[0],s[0],s[0],perm)
    t = _noise4a(s,s,s,s,perm)
    _noise4a_ip(s,s,s,s,perm,t)
    return True