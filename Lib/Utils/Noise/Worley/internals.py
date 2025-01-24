import numpy as np
import random
from math import floor , hypot, sqrt


__all__ = [
    'getAt',
    'getArr',
    'njit',
    'prange'
]

try:
    from numba import njit,prange,literal_unroll
except ImportError:
    def njit(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper  
    prange = range    
    literal_unroll = lambda x:x


def init(seed:int) -> np.ndarray:
    '''More or less copied from Simplex.internals.init '''
    from ctypes import c_int64
    def _overflow(x): return c_int64(x).value
    perm = np.zeros(256,dtype=np.uint64)
    source = np.arange(256)
    seed = _overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = _overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = _overflow(seed * 6364136223846793005 + 1442695040888963407)
    for i in range(255, -1, -1):
        seed = _overflow(seed * 6364136223846793005 + 1442695040888963407)
        r = int((seed + 31) % (i + 1))
        if r < 0:
            r += i + 1
        perm[i] = source[r]
        source[r] = source[i]
    perm = perm.astype(np.float64) / 256
    perm = 2 * perm * (1 - perm)
    return perm


### BEWARE ###
# There be dragons in the depths below

@njit(cache=True)
def _calculate_cell(x:int,y:int,perm:np.ndarray):
    i = (y + 13 * x) % perm.size
    i2 = ((0b101010101^y)-x+1) % perm.size
    i3 = ((y*17)^(x*3+77)) % perm.size
    a = perm[i]
    b = perm[i2] 
    c = perm[i3]
    return x + a + b,  y + a + c


@njit(cache=True)
def getAt(x:float,y:float,perm):
    cx = floor(x)
    cy = floor(y)
    shortest = 999.9
    for cx,cy in [(cx-1,cy-1),(cx,cy-1),(cx+1,cy-1),(cx-1,cy),(cx,cy),(cx+1,cy),(cx-1,cy+1),(cx,cy+1),(cx+1,cy+1)]:
        px,py = _calculate_cell(cx,cy,perm)
        d = hypot(px-x,py-y)
        if d < shortest:
            shortest = d
    return shortest/sqrt(2)

@njit(parallel = False,boundscheck = False)
def getArr(xs:np.ndarray,ys:np.ndarray,perm):
    noise = np.empty((ys.size, xs.size), dtype=np.float32)
    for y_i in prange(ys.size):
        for x_i in prange(xs.size):
            shortest_sqrd = 999.9
            cx_ = floor(xs[x_i])
            cy_ = floor(ys[y_i])
            for cx,cy in [(cx_-1,cy_-1),(cx_,cy_-1),(cx_+1,cy_-1),(cx_-1,cy_),(cx_,cy_),(cx_+1,cy_),(cx_-1,cy_+1),(cx_,cy_+1),(cx_+1,cy_+1)]:
                px,py = _calculate_cell(cx,cy,perm)
                dx = px-xs[x_i]
                dy = py-ys[y_i]
                shortest_sqrd = min(dx*dx+dy*dy,shortest_sqrd)
            noise[y_i, x_i] = sqrt(shortest_sqrd/2)
    return noise


