# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
import pygame
from pygame import sprite

logger = logging.getLogger(__name__)

from simplegame import utils

# ---------------------------------------------------------------------------
use_screen = object() # sentinel

class ImageSprite(sprite.Sprite):
    """ Abstract base class, factors out common parts of our game objects

    :param imagepath: the path to the image to load
    :param area: the containing :class:`pygame.Rect` area.
                 If not passed, the main `pygame.display` surface's `Rect`
                 will be used as area 

    
    :attr image: a :class:`pygame.image` instance
    :attr rect: a :class:`pygame.rect` for the :attr:`image`
    :attr area: the containing :class:`pygame.Rect` 
    """
    def __init__(self, imagepath, area=use_screen):
        super(ImageSprite, self).__init__()
        self.image, self.rect = utils.load_img(imagepath)
        if area is use_screen:
            area = pygame.display.get_surface().get_rect()
        self.area = area

    
