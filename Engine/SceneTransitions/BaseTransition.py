import pygame as pg 

class BaseTransition:
    def Step(self,surf:pg.Surface) -> bool: '''Returns whether scene transition is done'''; ...


    