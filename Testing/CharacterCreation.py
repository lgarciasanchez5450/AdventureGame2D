# from Utils.Math import game_math

import glm





# There will be a sort of convention to follow when creating a custom character or even an AliveEntity in the first place

# From now on the word "players" and such variations will be an alias for humanoid living entities in the general_manager

# first of all players need some sort of head
# secondly they all need a sort of body and appendages
# everything will be centered around the middle point of the body
# so the body will always be coordinate <0,0>
# making an example as a sort of sanity check:
# Player:
# - Body:
#    - Parent: None
#    - Position: <0,0>
#    - Rotation: 0 Radians
#    - Image path is ...\Images\...\.png
# - Head:
#    - Parent: Body
#    - Position: <0,3>
#    - Rotation: 0 Radians
#    - Image path : ....
# - Left Leg:
#    - Parent: Body
#    - Position: <-2,-3>
#    - Rotation: 0 Radians
#    - Image Path :  ....png
# - Right :
#    - Parent: Body
#    - Position: <2,-3>
#    - Rotation: 0 Radians
#    - Image Path: ...png


import pygame

screen = pygame.display.set_mode((900,600))

t = 0
clock = pygame.time.Clock()
class Head:
    def __init__(self,image):
        self.parent = None
        self.surf = pygame.transform.scale_by(image,2)


    def draw(self,offset):
        screen.blit(self.surf,offset)


class Node:
    def __init__(self,pos:glm.vec2):
        self.pos = pos

n_neck = Node(glm.vec2(0,1))
n_left_shoulder = Node(glm.vec2(-0.5,0.9))
n_right_shoulder = Node(glm.vec2(0.5,0.9))
n_left_leg_socket = Node(glm.vec2(-0.3,-0.2))
n_right_leg_socket = Node(glm.vec2(0.3,-0.2))
n_left_knee = Node(glm.vec2(-0.3,-0.75))
n_right_knee = Node(glm.vec2(0.3,-0.75))
n_left_foot = Node(glm.vec2(-0.3,-1.3))
n_right_foot = Node(glm.vec2(0.3,-1.3))

NODES = [n_neck,n_left_leg_socket,n_left_shoulder,n_right_leg_socket,n_right_shoulder,n_left_knee,n_right_knee,n_left_foot,n_right_foot]
        
def flipY(x:glm.vec2):
    return glm.vec2(x.x,-x.y)
    
def nodes_to_screen(*nodes:Node):
    for node in nodes:
        yield flipY(node.pos * size)

def draw_torso():
    pygame.draw.polygon(screen,'green',[(n+center).to_tuple() for n in nodes_to_screen(n_neck,n_right_shoulder,n_right_leg_socket,n_left_leg_socket,n_left_shoulder)])

size = 50
skin_color = (214,179,149)

def draw_head():
    head_radius = 17
    pygame.draw.circle(screen,skin_color,(next(nodes_to_screen(n_neck))+center-glm.vec2(0,head_radius-2)).to_tuple(),head_radius)
# print(draw_head())
head = Head(pygame.image.load('Assets/Entities/NewPlayer/NewPlayer/Bald Head_sprite_1.png'))
hair = Head(pygame.image.load('Assets/Entities/NewPlayer/NewPlayer/Hair_sprite_1.png'))
torso = Head(pygame.image.load('Assets/Entities/NewPlayer/NewPlayer/Torso_sprite_1.png'))
legs = Head(pygame.image.load('Assets/Entities/NewPlayer/NewPlayer/Legs_sprite_1.png'))


from math import sin,pi
t = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    screen.fill('black')
    x = 200
    y = round(sin(t)*3)*2+200
    center= glm.vec2(pygame.display.get_window_size())//2
    draw_torso()
    draw_head()
    for n in NODES:
        pos = glm.vec2(n.pos)
        pos.y = -pos.y

        pygame.draw.circle(screen,'white',glm.floor(center+pos*size).to_tuple(),1)
    legs.draw((x,y))
    torso.draw((x,y))
    head.draw((x,y))
    hair.draw((x,y))
    # print(y)
    pygame.draw.rect(screen,'white',(x,y,1,1))
    pygame.display.flip()
    clock.tick(30)
    t = pygame.time.get_ticks() / 1000
    # print(t)
