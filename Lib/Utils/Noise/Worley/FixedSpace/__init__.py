'''
Similar to Exterior "Worley" Package, except that this is worley noise for 
Fixed Spaces (e.g. a fixed size map of size <width> and <height>)
This module will offer "performance speedups"(?) and qualitative improvements 
over the infinite space Worley Package.
'''
import numpy as np


try:
    from numba import njit,prange,literal_unroll
except ImportError:
    def njit(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper  
    prange = range    
    literal_unroll = lambda x:x

class WorleyNoise:
    '''Currently is Slower than Infinite Space Worley Noise, However does have qualitative improvements over it.'''
    def __init__(self,seed:int,size:tuple[float,float]|tuple[float,float,float],density:float = 1):
        self.seed = seed
        self.size = size
        self.density = density
        #Num_Points = floor(Size[Area/Volume] * density / sqrt(2))

        self._num_points = int(np.floor(np.prod(self.size) * (density / np.sqrt(2))))
        r = np.random.Generator(np.random.MT19937(self.seed))
        self.points = r.random((self._num_points,len(size)))*np.array(size)



    def getArr(self,n:int):
        if len(self.size) == 2:
            return getArr2D(self.points,self.size,n)
        else:
            return getArr3D(self.points,self.size,n)
        
@njit
def relax_points(arr:np.ndarray,size:tuple[float,float],iters:int=10,coef:float = 5e-1):
    #create a similar array to represent velocities
    u_rad = 9
    vel = np.empty_like(arr,dtype=np.float32)
    for _ in range(iters):
        vel[:] = 0
        #distance to edge
        for i in range(arr.shape[0]):
            d0 = arr[i][0]
            ds = size[0]-arr[i][0]
            d0y = arr[i][1]
            dsy = size[1]-arr[i][1]
            vel[i][0] = np.exp(-np.abs(d0)/u_rad*2) - np.exp(-np.abs(ds)/u_rad*2)
            vel[i][1] = np.exp(-np.abs(d0y)/u_rad*2) - np.exp(-np.abs(dsy)/u_rad*2)
            # vel[i][:] = 0
            
            for j in range(arr.shape[0]):
                if i == j: continue
                dv:np.ndarray = (arr[i] - arr[j]) 
                d = np.sqrt(np.dot(dv,dv))
                a = np.exp(-d/u_rad)
                vel[i] += dv*a
        vel *= coef
        arr += vel
    return arr
        
@njit(boundscheck=False)
def kmin(arr:np.ndarray,k:int):
    if k == 0:
        return arr.min()
    t = np.sort(arr[:k+1])
    i = k+1
    while (i < arr.size):
        if arr[i] < t[-1]:
            x  = np.searchsorted(t,arr[i])
            val = arr[i]
            while (x < t.size):
                val,t[x] = t[x],val
                x += 1
        i+=1
    return t[-1]

@njit(parallel = True,boundscheck = False)
def getArr2D(points,size,n):
    noise = np.empty(size[::-1], dtype=np.float32)
    for y_i in prange(size[1]):
        for x_i in prange(size[0]):
            xy = np.array([x_i,y_i])
            a = points - xy
            a *= a
            a = np.sum(a,axis=1)
            nth = kmin(a,n)
            noise[y_i, x_i] = np.sqrt(nth)
    return noise

@njit(parallel = True,boundscheck = False)
def getArr3D(points,size,n):
    noise = np.empty(size[::-1], dtype=np.float32)
    for z_i in prange(size[2]):
        for y_i in prange(size[1]):
            for x_i in prange(size[0]):
                xy = np.array([x_i,y_i,z_i])
                a = points - xy
                a *= a
                a = np.sum(a,axis=1)
                nth = kmin(a,n)
                noise[z_i, y_i, x_i] = np.sqrt(nth)
    return noise

def tformat(x:float,sigfig:int=2):
    i = 0
    while x < 1:
        x *= 1000
        i += 1
    suf = ['s','ms','µs','ns']
    return f'{round(x,sigfig-1)} {suf[i]}'


if __name__ == "__main__":
    from time import perf_counter
    e = WorleyNoise(1,(600,600,90),0.00001)
    _ = WorleyNoise(1,(10,10,10),0.001).getArr(0)
    relax_points(np.empty((10,2)),(600,600),10,.5)
    print('Initialized')
    import pygame
    
    xs = np.arange(600)
    ys = np.arange(600)
    s = pygame.display.set_mode((600,600))
    from pygame.surfarray import blit_array
    def draw_n():
        global arr
        # s_ = perf_counter()
        # arr = e.getArr(n)
        if(len(arr.shape) == 3):
            ymax = arr.shape[0]
            a = arr[int(ymax*(np.sin(t)+1)/2)]
        else:
            a = arr
        # print(a)
        # e_ = perf_counter()
        # print(tformat(e_-s_))
        
        a = a * (255 / a.max())
        a:np.ndarray = a.astype(np.uint32)
        a |= (a << 8) | (a << 16) # convert to grayscale
        blit_array(s,a)
    n = 1 
    print('generating array')
    arr = e.getArr(n)
    t = 0
    tstart = perf_counter()
    draw_n()
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    n+=1
                    n = min(n,255)
                    arr = e.getArr(n)
                elif event.key == pygame.K_DOWN:
                    n-= 1
                    n = max(n,0)
                    arr = e.getArr(n)
                elif event.key == pygame.K_r:
                    relax_points(e.points,(600,600),10,.5)
                    arr = e.getArr(n)
            pygame.display.set_caption(str(n))

        draw_n()
        t = perf_counter() - tstart
        pygame.display.flip()

        pygame.time.Clock().tick(50)

        
