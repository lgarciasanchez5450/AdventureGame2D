import pygame
ENGINE = pygame.event.custom_type()

ENGINE_CLOSE = pygame.event.Event(ENGINE,{'close':True,'cleanup':True})
'''Gracefully Exit out of the Engine'''

ENGINE_KILL = pygame.event.Event(ENGINE,{'close':True,'cleanup':False})
'''Exit out of the Engine without cleanup'''
