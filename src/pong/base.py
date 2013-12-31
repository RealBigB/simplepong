# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

import os

from simplegame.sprites import ImageSprite as BaseImageSprite

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

class ImageSprite(BaseImageSprite):
    image = NotImplemented
    
    def __init__(self, area):
        super(ImageSprite, self).__init__(
            os.path.join(DATA_DIR, self.image),
            area
            )
        
