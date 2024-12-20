import typing
import pygame
import glm
import numpy as np
from Lib import Engine
from Lib.Engine.SceneTransitions.BaseTransition import BaseTransition
from Lib.Utils.debug import Tracer,LagTracker
from pygame import constants as const
from Entities.Entity import Entity, Block
from Scripts.EntityComponents import Animation
from Scenes.SceneComponents.TerrainGeneration import TerrainGen
from Scenes.SceneComponents.WorldManager import WorldManager

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
    def __init__(self,engine:Engine.Engine) -> None:
        self.engine = engine
        self.viewport_size = (800,500)
        self.world_surf = None

        self.invalid_chunk = np.zeros((8,8),dtype = np.uint8)
        
        self.world = WorldManager(8)
        self.world.setTerrainGenerationPipeline(TerrainGen(8))
        self.engine.target_fps = 0

        tiles = self.engine.resource_manager.getDir('NewTiles')
        e_tiles = self.engine.resource_manager.getDir('Entities/NewPlayer/PlayerFrontIdle')
        null_tex = pygame.transform.scale(self.engine.resource_manager.getTex('Ground/null.png'),(32,32))
        self.layer_entities = LayerYSort()

        self.player_speed = 4


        self.tiles = [null_tex]
        self.tiles.append(tiles['Water']['sprite_0.png']) #type: ignore
        self.tiles.append(tiles['Grass']['sprite_0.png']) #type: ignore
        self.tiles.extend(tiles['WaterBorderGrassBottom'].values()) #type: ignore
        self.tiles.extend(tiles['WaterBorderGrassTop'].values()) #type: ignore
        self.tiles = list(map(pygame.Surface.convert,self.tiles))
        self.e_tiles = []
        self.e_tiles.extend(e_tiles.values())
        self.e_tiles = list(map(pygame.Surface.convert,self.e_tiles))
        self.offsets = [(-11,-30)] * len(self.e_tiles)
        for s in self.e_tiles:
            s.set_colorkey((0,0,0))

        

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
        self.world.setComponent(self.player,Animation(self.player,[0,0,0,3,4,5,5,5,3],6))
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
        starting_pos = self.player_pos//8
        self.player_pos += vel * (dt * self.player_speed)
        if self.player_pos//8 != starting_pos:
            self.recalcChunks()

        #move camera
        camera_adjust_rate = 0.1 #[0,1]
        self.camera_position += (self.player_pos - self.camera_position) * camera_adjust_rate

        self.world.update(dt)
        for comp in self.world.e_components[Animation.i].values(): #type: ignore
            comp:Animation
            comp.t += dt * comp.fps
            comp.entity.renderid = comp.cycle[comp.t.__trunc__()%len(comp.cycle)]


        #update miscellaneous stuff
        
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
            chunk = self.world.entity_chunks.get(cpos,[])
            chunk.sort(key=lambda x: x.position.y)
            for entity in chunk:
                x,y = glm.floor((entity.position - self.camera_position)*32)
                ox,oy = self.offsets[entity.renderid]
                self.world_surf.blit(self.e_tiles[entity.renderid],(x.__floor__()+hx+ox.__floor__(),y+hy+oy))

            # if cx < -32*chunk_size or cy < -32*chunk_size or cx >= vw or cy >= vh: continue
        
        lag.draw(screen,(0,screen.get_height()-lag.get_height()))
            
        # self.world_surf.fblits([(self.tiles[renderid],glm.ivec2(pos).to_tuple()) for pos,renderid in self.layer_entities.getDrawList(self.camera_position)])
            

    def stop(self):
        print('stop called')

    def release(self):
        self.world.release()
        print('release called')

