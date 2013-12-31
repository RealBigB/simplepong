# -*- coding: utf-8 -*-
""" Simple pygame pong game.

Custom events and event-related stuff
"""
import logging
import os
import random
import math

import pygame
#from pygame import sprite
#from pygame import locals 

from simplegame.base import GameProperty
from simplegame.sprites import ImageSprite

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom events
# ---------------------------------------------------------------------------
OFFCOURT = pygame.USEREVENT + 1 # what's wrong with 42 ?
def BallOffCourt(side, last_hit_by):
    return pygame.event.Event(OFFCOURT, side=side, last_hit_by=last_hit_by)
