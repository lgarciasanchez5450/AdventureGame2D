import typing
import pygame
import glm
import numpy as np
from Lib import Engine
from Lib.Engine.SceneTransitions.BaseTransition import BaseTransition
from Lib.Utils.debug import Tracer,LagTracker
from pygame import constants as const
from Entities.Entity import Entity, Block
from Scripts import EntityComponents as EC
from Scripts.GameSeed import GameSeed
from Scripts.BackgroundAnim import BackgroundAnim
from Scenes.SceneComponents.TerrainGeneration import TerrainGen
from Scenes.SceneComponents import TerrainGeneration
from Scenes.SceneComponents.WorldManager import WorldManager
from Scripts.WorldGenContext import WorldGenContext
from Lib.Utils.Math.game_math import expDecay


class DrawComponent(typing.Protocol):
    position:glm.vec2
    renderid:int
lag = LagTracker()
class Layer:
    def __init__(self,max_drawables:int=-1):
        self.drawables:list[DrawComponent] = []
        self.max = max_drawables

    def addDrawable(self,drawcomp:DrawComponent):
        if len(self.drawables) == self.max: return False
        self.drawables.append(drawcomp)
        return True
    
    def removeDrawable(self,drawcomp:DrawComponent):
        if len(self.drawables) == 0: return False
        self.drawables.remove(drawcomp)
        return True
    
    def getDrawList(self,cam_pos:glm.vec2):
        for drawable in self.drawables:
            yield glm.floor((drawable.position - cam_pos) * 32),drawable.renderid

class LayerYSort(Layer):
    def getDrawList(self,cam_pos:glm.vec2):
        self.drawables.sort(key = lambda x:x.position.y)
        return super().getDrawList(cam_pos)

class World(Engine.BaseScene):
    '''
    Should not hold any game state data
    '''
    def __init__(self,engine:Engine.Engine,game_seed:GameSeed) -> None:
        self.engine = engine
        self.viewport_size = (800,500)
        self.world_surf = None

        self.invalid_chunk = np.zeros((8,8),dtype = np.uint8)
        
        self.world = WorldManager(game_seed,8)
        with WorldGenContext(game_seed).context(TerrainGeneration.__dict__):
            self.world.setTerrainGenerationPipeline(TerrainGen(8)) #type: ignore
        self.engine.setFPS(60)

        tiles = self.engine.resource_manager.getDir('NewTiles')
        e_tiles = self.engine.resource_manager.getDir('Entities/NewPlayer/PlayerFrontIdle')
        null_tex = pygame.transform.scale(self.engine.resource_manager.getTex('Ground/null.png'),(32,32)).convert()
        self.player_speed = 4
        bg_anim = BackgroundAnim(10)
        bg_anim.addStill(null_tex)
        bg_anim.addAnim([tiles['Water']['sprite_0.png'].convert()],10)#type: ignore
        bg_anim.addAnim([tiles['Grass']['sprite_0.png'].convert()],10)#type: ignore
        bg_anim.addAnim([s.convert() for s in tiles['WaterBorderGrassBottom'].values()],10)#type: ignore
        bg_anim.addAnim([s.convert() for s in tiles['WaterBorderGrassTop'].values()],10)#type: ignore


        self.bg_tiles = bg_anim.build()
        # self.tiles = list(map(pygame.Surface.convert,self.tiles))
        self.e_tiles = []
        self.e_tiles.extend(e_tiles.values())
        self.e_tiles = list(map(pygame.Surface.convert,self.e_tiles))
        for s in self.e_tiles: s.set_colorkey((0,0,0))

        self.offsets = [(-11,-30)] * len(self.e_tiles)

        self.player = Entity((0,0),(1,1),1)
        self.player_pos = self.player.position
        self.camera_position = glm.vec2(self.player_pos)
        self.recalcChunks()


    @Tracer().trace
    def recalcChunks(self):
        c = glm.ivec2(self.player_pos//8)
        new = {(x,y) for x in range(c.x-3,c.x+4,1) for y in range(c.y-2,c.y+3,1)}

        self.world.loadChunks(new)
        self.world.setActiveChunks(new)

    def start(self):
        print('Start called')
        #spawn player entity
        self.world.spawnEntity(self.player)
        self.world.setComponent(self.player,EC.Animation(self.player,[0,0,0,3,4,5,5,5,3],6))


    @Tracer().traceas("SceneUpdate")
    def update(self):
        #process events
        dt = self.engine.time.dt
        pygame.display.set_caption(f'{self.engine.time.getFPS():.2f}')
        for event in self.getEvents():
            if event.type == const.QUIT:
                pygame.event.post(Engine.Settings.ENGINE_CLOSE)
            elif event.type == const.WINDOWRESIZED:
                self.world_surf = None 
        lag.add(self.engine.time.unscaledDeltaTime)
        # keys_d = pygame.key.get_just_pressed()
        
        #move character
        keys = pygame.key.get_pressed()
        # self.engine.tracer.running = keys[const.K_t]
        
        w = keys[const.K_w]
        a = keys[const.K_a]
        s = keys[const.K_s]
        d = keys[const.K_d]
        
        vel = glm.vec2(d-a,s-w)
        if vel.x and vel.y:
            vel = glm.normalize(vel)
        self.player.vel = vel
        starting_pos = self.player_pos//8


        #move camera
        convergence_rate = 2 #[1,25] slow to fast
        self.camera_position = expDecay(self.camera_position,self.player_pos,convergence_rate,dt)


        self.world.update(dt)
        for comp in self.world.iterComponents(EC.Animation): 
            comp.t += dt * comp.fps
            comp.entity.renderid = comp.cycle[comp.t.__trunc__()%len(comp.cycle)]


        if self.player_pos//8 != starting_pos:
            self.recalcChunks()

        #update miscellaneous stuff

        self.tiles = self.bg_tiles.get_tiles(dt)
        
    @Tracer().trace
    def draw(self,screen:pygame.Surface):
        '''
        Optmized Drawing Routine for drawing and culling ground tiles
        '''
        if self.world_surf is None:
            self.world_surf = screen.subsurface((screen.get_width()-self.viewport_size[0])//2,(screen.get_height()-self.viewport_size[1])//2,self.viewport_size[0],self.viewport_size[1])
        screen.fill('black')
        vw = self.viewport_size[0]
        vh = self.viewport_size[1]
        l:list[tuple[pygame.Surface,tuple[int,int]]] = []
        hx = vw//2
        hy = vh//2
        chunk_size = self.world.chunk_size
        for cpos in self.world.active_chunks:
            chunk = self.world.terrain_chunks.get(cpos,self.invalid_chunk)
            cx = cpos[0] * 8 - self.camera_position.x
            cy = cpos[1] * 8 - self.camera_position.y
            if cx < -32*chunk_size or cy < -32*chunk_size or cx >= vw or cy >= vh: continue
            for x in range(chunk_size):
                px = ((cx+x)*32).__floor__() + hx
                if px < -32 or px >= vw: continue
                for y in range(chunk_size):
                    py = ((cy+y)*32).__floor__() + hy
                    if -32 <= py < vh:
                        l.append((
                            self.tiles[chunk[x,y]],
                            (px,py)
                        ))

        self.world_surf.fblits(l)

        ## Start Unoptimized portion ##
        for cpos in sorted(self.world.active_chunks,key=lambda x: x[1]):
            chunk = self.world.entity_chunks.get(cpos)
            if chunk is None: continue
            chunk.sort(key=lambda x: x.position.y)
            for entity in chunk:
                x,y = glm.floor((entity.position - self.camera_position)*32)
                ox,oy = self.offsets[entity.renderid]
                self.world_surf.blit(self.e_tiles[entity.renderid],(x+hx+ox,y+hy+oy))

            # if cx < -32*chunk_size or cy < -32*chunk_size or cx >= vw or cy >= vh: continue
        
        lag.draw(screen,(0,screen.get_height()-lag.get_height()))
            
            

    def stop(self):
        print('stop called')

    def release(self):
        self.world.release()
        print('release called')

