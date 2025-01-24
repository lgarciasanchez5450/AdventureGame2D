try:from Scripts.GameSeed import GameSeed
except: from GameSeed import GameSeed

from Lib.Utils.Noise.Simplex import OpenSimplexLayered,preinitialize


from Lib.Engine import PreInitialization

PreInitialization.addInitialization(preinitialize)

class WorldGenContext:
    __slots__ = 'height','rainfall','temperature'
    def __init__(self,game_seed:GameSeed):
        self.height = OpenSimplexLayered(game_seed.seed,4)
        self.rainfall = OpenSimplexLayered(game_seed.seed+1,2)
        self.temperature = OpenSimplexLayered(game_seed.seed+2,2)

    def context(self,locals:dict):
        class Context:
            def __enter__(self2): #type: ignore
                locals['context'] = self
            def __exit__(self2,type_: type[BaseException]|None,value:BaseException|None,traceback): #type: ignore
                return False
        return Context()

