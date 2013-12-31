# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

import pygame
from pygame.locals import * # XXX

from simplegame.base import State

from pong.states.base import BallStrategy, RunningState
from pong.states.playing import Playing
from pong.states.service import Service

__all__ = ["Intro", "Party", "Service", "Playing", "Paused", "Won",] 


# ---------------------------------------------------------------------------
class Intro(State):
    NAME = 'intro'

# ---------------------------------------------------------------------------
class Party(State):
    NAME = 'party'
    
# ---------------------------------------------------------------------------
class Won(State):
    NAME = 'won'

# ---------------------------------------------------------------------------
class Paused(RunningState):
    NAME = 'paused'

    def on_keyup(self, event):
        if event.key == K_SPACE:
            logger.debug("Pause -> playing")
            self.game.goto("playing")
            self.done = True

    def updatespites(self):
        pass
