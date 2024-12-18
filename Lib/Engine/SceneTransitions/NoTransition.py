from SceneTransitions.BaseTransition import BaseTransition
import pygame as pg
class NoTransition(BaseTransition):
    def Step(self,surf:pg.Surface):
        return True