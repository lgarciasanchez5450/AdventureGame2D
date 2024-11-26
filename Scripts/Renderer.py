from typing import Protocol
import pygame as pg
import builtins
from Scripts.Chunk import Chunk
import glm
class Coordinate(Protocol):
    def __mul__(self,other:float) -> 'Coordinate': ...
    def __truediv__(self,other:float) -> 'Coordinate': ...
    def __getitem__(self,index:int) -> float|int: ...
    def __setitem__(self,index:int,value:float|int): ...

class Camera(Protocol):
    position:glm.vec2
class Renderer:
    '''
    Responsible for Drawing Every Diagetic object to Screen
    there will be two coordinate planes, 
    Pixel and World
    in Pixel Space each unit is defined to be the size of 1 pixel
    in World Space each unit is defined to be n amount of Pixel Space Units, where n is defined by <block_size>
    '''

    def __init__(self,camera:Camera,chunks:dict[tuple[int,int],Chunk]) -> None:
        self.block_size = 16
        self.camera = camera
        self.chunks = chunks

    def setCamera(self,camera:Camera):
        self.camera = camera
        
    def draw(self):
        pixels_per_chunk = self.block_size * Chunk.SIZE #pixels per block * blocks per chunk
        viewport_size = glm.ivec2(800,600)
        import pygame
        surf = pygame.Surface(viewport_size.to_tuple())
        #draw floor, then draw entities and particles
        camera_position = self.camera.position
        # camera_cpos = glm.ivec2(self.scene.camera.position//Chunk.SIZE).to_tuple()
        leftmost_chunk = camera_position.x - viewport_size.x/(2*self.block_size)
        rightmost_chunk = camera_position.x + viewport_size.x/(2*self.block_size)
        topmost_chunk = camera_position.y - viewport_size.y/(2*self.block_size)
        bottommost_chunk = camera_position.y + viewport_size.y/(2*self.block_size)
        from Utils.Math.game_math import collide_chunks2d
        camera_pixel_coords = glm.ivec2(glm.floor(camera_position * self.block_size))
        for cpos in collide_chunks2d(leftmost_chunk//Chunk.SIZE,topmost_chunk//Chunk.SIZE,rightmost_chunk//Chunk.SIZE,bottommost_chunk//Chunk.SIZE,Chunk.SIZE):
            chunk_pixels_coords = glm.ivec2(cpos) * pixels_per_chunk
            screen_position = chunk_pixels_coords - camera_pixel_coords
            surf.b

    def world(self,pixel_coords:Coordinate):
        return pixel_coords / self.block_size
    
    def pixel(self,world_coords:Coordinate):
        return world_coords * self.block_size