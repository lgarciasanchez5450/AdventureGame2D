import Engine
from Scenes.World import World

class Application:
    def run(self): ...





class GameApp(Application): 
    def __init__(self) -> None:
        self.engine = Engine.Engine()
        self.engine.sceneCreator = self.createScenes

    def createScenes(self):
        return {'scene1':World(self.engine)}

    
    def run(self):
        self.screen = Engine.pg.display.set_mode((900,600),Engine.const.RESIZABLE)
        if not self.engine.Start():  
            return False
        return self.engine.Run()
   
if __name__ == '__main__':
    app:Application = GameApp()
    print('Game Instantiated')
    app.run()
