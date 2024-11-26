import Engine

class Application:
    def run(self): ...

class GameApp(Application): 
    def __init__(self) -> None:
        self.engine = Engine.Engine()  
    
    def run(self):
        self.screen = Engine.pg.display.set_mode((900,600),Engine.const.RESIZABLE)

        if not self.engine.Start():
            return False
        return self.engine.Run()
   
        
if __name__ == '__main__':
    app:Application = GameApp()
    print('Game Instantiated')
    app.run()
