import typing
import glm

type CPOS = tuple[int,int]

class Weather:
    '''
    Provides weather information on a per chunk and sometimes per block basis
     Provides information on: 
     * Temperature
     * Wind Velocity
     * Humidity
     * Rain
    
    '''
    def __init__(self):
        pass

    def getTemperature(self,cpos:CPOS):
        '''Returns: Temperature in celsius'''
        t = 20
        return t

    def getWindVelocity(self,cpos:CPOS):
        '''Returns: Velocity in Blocks Per Second'''
        return glm.vec2(.1,.1)
    
    def getHumidity(self,cpos:CPOS):
        '''Returns: Humidity as a percentage of maximum moisture that the air can hold'''
        return 0.65
    
    def update(self):
        pass

