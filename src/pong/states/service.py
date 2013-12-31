# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

import random
import math

import pygame
from pygame import sprite
from pygame.locals import * # XXX

from pong.events import BallOffCourt, OFFCOURT
from pong.widgets import ServiceText
from pong.states.base import BallStrategy, RunningState

# ---------------------------------------------------------------------------
class ServiceStrategy(BallStrategy):
    """ A ball sticking to a :class:Bat` """

    def reinit(self):
        self.ball.rect = self.get_ball_rect_for_player(self.ball, self.player1)
        self.ball.last_hit_by = self.player1
        
    def update(self):
        self.ball.rect = self.get_ball_rect_for_player(self.ball, self.player1)
      
# ---------------------------------------------------------------------------
class Service(RunningState):
    NAME = 'service'
    
    BALL_STRATEGY = ServiceStrategy

    def on_init(self):
        super(Service, self).on_init()
        self.text = ServiceText("Press space to start", self.screen, self.background)
        
    def on_start(self, resume):
        super(Service, self).on_start(resume)
        self.ball.reinit(self)
        for player in self.players:
            player.reinit(self)
       
    def on_keydown(self, event):
        # XXX quelque chose de plus élégant ?
        if event.key == K_a:
            self.player1.moveup()
        elif event.key == K_q:
            self.player1.movedown()
        elif event.key == K_UP:
            self.player2.moveup()
        elif event.key == K_DOWN:
            self.player2.movedown()

    def on_keyup(self, event):
        if event.key == K_SPACE:
            self.goto("playing")
            return
        
        elif event.key == K_a or event.key == K_q:
            self.player1.still()
        elif event.key == K_UP or event.key == K_DOWN:
            self.player2.still()

    def on_render(self):
        self.text.draw()
        super(Service, self).on_render()

    def on_done(self):
        self.text.clear()
        super(Service, self).on_done()

