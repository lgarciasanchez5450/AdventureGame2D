import typing
import glm
import numpy as np
import numpy.typing as npt
from Lib.Utils.Noise.Simplex import OpenSimplex
from Scripts.GameSeed import GameSeed

type CPOS = tuple[int,int]
'''
Each Weather Chunk is twice as long and wide as a terrain chunk
'''

class Weather:
    '''
    Provides local and global weather information on a per chunk and sometimes per block basis
     Provides information on: 
     * Temperature
     * Wind Velocity
     * Humidity
     * Precipitation
    
    '''
    __slots__ = 'time_of_day','_noise','humidity','temperature','g_wind_dir','g_wind_str','t','seed'
    def __init__(self,seed:GameSeed):
        self.seed = seed.seed
        self._noise = OpenSimplex(seed.seed)
        self.humidity:dict[CPOS,float] = {}
        self.temperature:dict[CPOS,float] = {}
        self.time_of_day = 0
        self.g_wind_dir = 0#in radians
        self.g_wind_str = 0
        self.t = 0

    def getTemperature(self,cpos:CPOS):
        '''Returns: Temperature in celsius'''
        return self.temperature[cpos]

    def getWindVelocity(self,cpos:CPOS):
        '''Returns: Velocity Vector in Blocks Per Second'''
        return glm.vec2(np.cos(self.g_wind_dir),np.sin(self.g_wind_dir)) * self.g_wind_str
    
    def getHumidity(self,cpos:CPOS):
        '''Returns: Humidity as a percentage of maximum moisture that the air can hold'''
        return self.humidity[cpos]
    
    def getPrecipitation(self,cpos:CPOS):
        '''Returns: Precipitation as a percentage of how much it is raining , 0 -> No rain, 1 -> Max Rain'''
        return 0
    
    def update(self,dt:float):
        self.t += dt
        self.g_wind_dir += self._noise.noise2(self.t,self.seed)
        self.g_wind_str = 2 * self._noise.noise2(self.t,self.seed+10)**2

    

if __name__ == '__main__':
    import pygame as pg
    
    screen = pg.display.set_mode((500,500))
    while True:
        pg.event.pump() 
        
        pg.display.flip()