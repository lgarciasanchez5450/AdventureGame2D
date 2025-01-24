import json

class GameSeed:
    seed:int
    #Global Save Info
    time_of_day:int
    time_scale:int

    #GameRules
    doDaylightCycle:bool 
    tickSpeed:int

    
    def toDict(self) -> dict:
        return self.__dict__.copy()
    
    @classmethod
    def fromDict(cls,d:dict):
        #make sure that it has all the keys necessary
        if not all(key in d for key in ['seed','time_of_day','doDaylightCycle','tickSpeed']): 
            raise KeyError("Missing Value in Game Seed!")
        o = GameSeed()
        o.__dict__ = d.copy()
        return o
    
    def toBytes(self) -> bytes:
        return json.dumps(self.toDict()).encode('utf-8')
    
    @classmethod
    def fromBytes(cls,b:bytes):
        return cls.fromDict(json.loads(b))

    @classmethod
    def newDefault(cls,seed:int):
        return cls.fromDict({
            'seed':seed,
            'time_of_day':300,
            'time_scale':1,
            'doDaylightCycle':True,
            'tickSpeed':20
        })


if __name__ == '__main__':
    g_seed = GameSeed.newDefault(1)
    print(g_seed.toBytes())

# A "Game" is a full context that includes a:
# Game Seed (integer), GameRules(dictionary), Optional[Terrain chunks, Weather chunks]