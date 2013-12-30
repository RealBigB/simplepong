# -*- coding: utf-8 -*-
""" utility functions and stuff
"""
import logging
import os
import sys

import pygame

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper functions and classes
# ---------------------------------------------------------------------------
def load_img(path):
    """ Load image from `path` and return
    a converted pygame image object and it's rect

    :param path: the path to the image file
    :return: a (:class:`pygame.image`, :class:`pygame:Rect`) tuple
    """
    try:
        image = pygame.image.load(path)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as e:
        logger.exception('Cannot load image:', fullname)
        raise
    return image, image.get_rect()
