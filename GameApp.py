from Lib import Engine
from Scenes.World import World
from Scripts.GameSeed import GameSeed

class Application:
    def run(self): ...


class GameApp(Application): 
    def __init__(self,game_seed:GameSeed) -> None:
        self.engine = Engine.Engine()
        self.engine.sceneCreator = self.createScenes
        self.game_seed = game_seed

    def createScenes(self):
        return {'scene1':World(self.engine,self.game_seed)}
    
    def run(self):
        self.screen = Engine.pg.display.set_mode((900,600),Engine.const.RESIZABLE)
        if not self.engine.Start():  
            return False
        return self.engine.Run()
   
if __name__ == '__main__':
    Engine.IgnoreScreenScaling()
    app:Application = GameApp(GameSeed.newDefault(0xfed))
    print('Game Instantiated')
    app.run()
