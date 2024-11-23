import glm
import typing
import pygame
from pygame import constants as const
from Scripts.Chunk import Chunk
from Scripts.LivingEntity import AliveEntity
if typing.TYPE_CHECKING:
    from GameApp import Engine
    from GameApp import RasterScene,RayTraceScene
NEAR = .1
FAR = 1024

class RasterCamera:
    def __init__(self,scene:"RasterScene",position) -> None:
        engine = self.scene.engine
        self.speed = 10
        self.scene = scene
        self.position = glm.vec3(position)
        self.yaw=0
        self.pitch = 0
        self.forward = glm.vec3(0,0,-1)
        self.right  = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
        self.xz_forward = glm.cross(glm.vec3(0,1,0),self.right)
        self.engine = engine
        self.aspect_ratio = 16/9#engine.window_size[0] / engine.window_size[1]
        self.real_fov = 90
        self.target_fov = 90 #allows for smoothly transitioning between fovs
        self.up = glm.vec3(0,0,1)
        self.m_view = self.get_view_matrix()
        self.m_projection = self.get_projection_matrix()
        self.last = self.position // Chunk.SIZE


    def update(self):
        rel_x, rel_y = pygame.mouse.get_rel()
        self.yaw += rel_x * 0.1
        self.pitch -= rel_y * 0.1
        self.yaw = self.yaw % 360
        self.pitch = max(-89, min(89, self.pitch))


        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
        self.xz_forward.x = glm.cos(yaw)
        self.xz_forward.z = glm.sin(yaw)
        self.forward.x = self.xz_forward.x * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = self.xz_forward.z * glm.cos(pitch)        
        self.forward = glm.normalize(self.forward)
        self.right.x = -glm.sin(yaw)
        self.right.y = glm.cos(yaw)
        # self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0,1,0)))
        self.up = glm.cross(self.right, self.forward)
        self.right = glm.cross(self.forward,self.up)

        if self.real_fov != self.target_fov:
            self.real_fov += (self.target_fov - self.real_fov) * self.engine.time.dt
            if abs(self.real_fov - self.target_fov) < 1:
                self.real_fov = self.target_fov
            self.m_projection = self.get_projection_matrix()
        self.m_view = self.get_view_matrix()
        self.check_chunk_cross()

    def check_chunk_cross(self):
        cpos = self.position//Chunk.SIZE
        if self.last != cpos:
            self.scene.chunk_manager.recalculateActiveChunks(*cpos)
            self.last = cpos

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)
    
    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.real_fov), self.aspect_ratio, NEAR, FAR)
    

    def move(self):...
    #     xz_movement = self.right * (self.engine.keys[const.K_d] - self.engine.keys[const.K_a]) + self.forward * (self.engine.keys[const.K_w] - self.engine.keys[const.K_s])

    #     if glm.length(xz_movement):
    #         xz_movement = glm.normalize(xz_movement)
        
    #     out = xz_movement + glm.vec3(0,1,0)* (self.engine.keys[const.K_SPACE]- self.engine.keys[const.K_LSHIFT]) 
    #     self.position += out * self.engine.time.dt

class EntityCamera(RasterCamera):
    def __init__(self,scene:"RasterScene",entity:AliveEntity):
        super().__init__(scene,entity.pos)
        self.position = entity.pos
        self.entity = entity

    def update(self):
        super().update()
        self.entity.forward = self.xz_forward
        self.entity.face_dir = self.forward
        self.entity.right = self.right



class RayTraceCamera:
    def __init__(self,scene:"RayTraceScene",position:tuple[int,int,int]) -> None:
        self.pos= glm.vec3(position)
        self.position = self.pos
        self.scene = scene
        self.engine = scene.engine
        self.yaw = 45
        self.pitch = -32
        self.xz_forward = glm.vec3()
        self.forward = glm.vec3()
        yaw = glm.radians(self.yaw)
        pitch = glm.radians(self.pitch)
        self.xz_forward.x = glm.cos(yaw)
        self.xz_forward.z = glm.sin(yaw)
        self.forward.x = self.xz_forward.x * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = self.xz_forward.z * glm.cos(pitch) 
        self.right  = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
       
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        self.position = self.pos
        rel_x, rel_y = pygame.mouse.get_rel()
        self.yaw += rel_x * 0.1
        self.pitch -= rel_y * 0.1
        self.pitch = min(max(self.pitch,-90),90)
        self.yaw %= 360
        yaw = glm.radians(self.yaw)
        pitch = glm.radians(self.pitch)
        self.xz_forward.x = glm.cos(yaw)
        self.xz_forward.z = glm.sin(yaw)
        self.forward.x = self.xz_forward.x * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = self.xz_forward.z * glm.cos(pitch) 
        self.right  = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
       
        self.up = glm.normalize(glm.cross(self.right, self.forward))
        # print(self.up)