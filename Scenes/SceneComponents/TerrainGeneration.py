import typing
import numpy as np
import numpy.typing as npt
from Lib.Utils.Pipeline import PipelineLayer,PipelineLayerMultiStep
from Lib.Utils.Noise.Simplex import OpenSimplexLayered,OpenSimplex
from Scripts.WorldGenContext import WorldGenContext


SCALE = 0.06


context:WorldGenContext|None = None
    
class HeightMapLayer(PipelineLayer[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]]):
    __slots__ = 'chunk_size','noise'
    def __init__(self,chunk_size:int, callback: typing.Callable[[typing.Mapping[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]], typing.Any] | None = None):
        super().__init__(callback)
        global context
        assert context is not None
        self.chunk_size = chunk_size
        self.noise = context.height

    def step(self,cpos:tuple[int,int]):
        xs = np.arange(self.chunk_size) + cpos[0] * self.chunk_size
        ys = np.arange(self.chunk_size) + cpos[1] * self.chunk_size
        return self.noise.noise2array(xs* SCALE,ys* SCALE).T

class RainfallMapLayer(PipelineLayer[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]]):
    __slots__ = 'chunk_size','noise'
    def __init__(self,chunk_size:int, callback: typing.Callable[[typing.Mapping[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]], typing.Any] | None = None):
        super().__init__(callback)
        global context
        assert context is not None
        self.chunk_size = chunk_size
        self.noise = context.rainfall

    def step(self,cpos:tuple[int,int]):
        xs = np.arange(self.chunk_size) + cpos[0] * self.chunk_size
        ys = np.arange(self.chunk_size) + cpos[1] * self.chunk_size
        return self.noise.noise2array(xs* SCALE,ys* SCALE).T
    
class TemperatureLayer(PipelineLayer[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]]):
    __slots__ = 'chunk_size','noise'
    def __init__(self,chunk_size:int, callback: typing.Callable[[typing.Mapping[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]], typing.Any] | None = None):
        super().__init__(callback)
        global context
        assert context is not None
        self.chunk_size = chunk_size
        self.noise = context.temperature

    def step(self,cpos:tuple[int,int]):
        xs = np.arange(self.chunk_size) + cpos[0] * self.chunk_size
        ys = np.arange(self.chunk_size) + cpos[1] * self.chunk_size
        return self.noise.noise2array(xs* SCALE,ys* SCALE).T


class TerrainGen(PipelineLayer[tuple[int,int],npt.NDArray[np.unsignedinteger[typing.Any]]]):
    @staticmethod
    def height_to_block(height:np.ndarray):
        # normalize to [0,1]
        height = (height + 1) / 2
        arr = np.empty_like(height,dtype=np.uint16)
        water_height = 0.5
        arr[height <water_height] = 1
        arr[np.logical_not(height <water_height)] = 2
        return arr
    
    def __init__(self,chunk_size:int,callback:typing.Callable[[typing.Mapping[tuple[int,int],np.ndarray]],typing.Any]|None=None):
        super().__init__(callback)
        self.chunk_size = chunk_size
        self.dependency_terrain_input:dict[tuple[int,int],tuple[np.ndarray,np.ndarray,np.ndarray]] = dict()
        self.dependency_terrain:NewTerrainLayer = NewTerrainLayer(chunk_size,self.dependency_terrain_input.update)
        self.current = None

    def declareDependencies(self, key: tuple[int, int]):
        self.dependency_terrain.addWork(key)

    def updateDependencies(self):
        self.dependency_terrain.update()

    def step(self,current:tuple[int,int]):
        terrain = self.dependency_terrain_input.get(current)
        #other dependencies go  here

        #make sure we have the dependencies we need for this chunk
        if terrain is not None:
            #safe to proceed
            xs,ys,height = terrain
            return self.height_to_block(height)

#Generation of the World should help the main purpose of this game which is to tell a story
#What is the moral of the story? its impossible to determine precise nature of things which are as complicated as morality and the human minds, to take a peek at the true nature you have to work backwards from the obvious (what you see, think, feel) to the hidden (values/virtues, what is good/evil?)
#Motto: Working Backwards
#Main Gameplay? Well the game should basically support 2 main types of gameplay. 
# 1) There should be a main storyline that you can play. You should be able to grow (and feel!!! meaningfully)stronger.
#   there should be many types of enemies that you can play against and mini-bosses, with lots of paths of growth
# 2) Farming Simulator(Stardew Valley-ish Relaxing Game): there should be an extensive path to grow crops and devices that faciliate farming (and optionally become rich?)
#   Farming should feel satisfying

#Terrain Generation should support the gameplay so.. 
# Most gameplay is on land so oceans should be kept to a minimum
# Because we are limited to 2 levels of ground there should be large patches of land with interesting groundwork
# Weather biomes should go crazy on land
type terrainType = npt.NDArray[np.unsignedinteger[typing.Any]]
type humidityType = float
type temperatureType = float

class WorldGen(PipelineLayerMultiStep[tuple[int,int],tuple[terrainType,humidityType,temperatureType]]):
    def __init__(self,chunk_size:int,
                 terrain:typing.Callable[[typing.Mapping[tuple[int,int],terrainType]],typing.Any],
                 humidity:typing.Callable[[typing.Mapping[tuple[int,int],humidityType]],typing.Any],
                 temperature:typing.Callable[[typing.Mapping[tuple[int,int],temperatureType]],typing.Any]
                 ):
        def combine_callbacks(a:typing.Mapping[tuple[int,int],tuple[terrainType,humidityType,temperatureType]]):
            t = {}
            h = {}
            t2 = {}
            for cpos,(ter,hum,tmp) in a.items():
                t[cpos] = ter
                h[cpos] = hum
                t2[cpos] = tmp
            terrain(t)
            humidity(h)
            temperature(t2)
        super().__init__(combine_callbacks)
        self.chunk_size = chunk_size
        assert context is not None
        self.n_height = context.height
        self.n_rain = context.rainfall
        self.n_temp = context.temperature
        self.sea_level = -0.1

    def step(self, cpos: tuple[int, int]) -> typing.Generator[None, None, tuple[terrainType, float, float]]:
        xs = np.arange(self.chunk_size) + cpos[0] * self.chunk_size
        ys = np.arange(self.chunk_size) + cpos[1] * self.chunk_size

        heightmap = self.n_height.noise2array(xs*SCALE,ys*SCALE)
        yield
        rainfall = self.n_rain.noise2array(xs*SCALE*0.5,ys*SCALE*0.5)
        yield
        temperature = self.n_temp.noise2array(xs*SCALE,ys*SCALE)
        
        #humidity must be proportional to the amount of rainfall and how close the terrain is to sea level
        #set the sea_level to be the new zero
        humidity_offset = heightmap - self.sea_level
        #square it to be positive values
        humidity_offset *= humidity_offset #maximum value that can exist in this array is (1 + self.sea_level)^2
        humidity_offset /= (1+self.sea_level)**2
        humidity = rainfall - humidity_offset

