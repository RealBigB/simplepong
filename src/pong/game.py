# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
import os
import random
import math

import pygame
from pygame import sprite
from pygame.locals import * # XXX

from simplegame.base import Game, GameProperty
from simplegame.sprites import ImageSprite

from pong.states import Intro, Party, Service, Playing, Paused, Won
from pong.objects import ScoreBoard, Bat, Ball
from pong.events import OFFCOURT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# The game
# ---------------------------------------------------------------------------
class Pong(Game):
    STATES = (
        #Intro,
        #Party,
        Service,
        Playing,
        Paused,
        Won
        )

    INITIAL_STATE = "service"
    SCREEN_SIZE = (640, 480)
    FPS = 60.
    
    OPTIONS_DEFAULTS = {
        "bgcolor" : (0, 0, 0),
        "speed" : 13,
        "angle": 0.47,
        "caption": "Basic Pong",
        # A suivre
        }

    ALLOWED_EVENTS = [
        QUIT, # obviously
        KEYUP, KEYDOWN,
        USEREVENT, OFFCOURT
        ]
    
    def before_init_states(self):
        self.court = self.screen.get_rect()
        self.scoreboard = ScoreBoard(self)

        self.players = tuple(Bat(side, player, self.court) for player, side in enumerate(Bat.SIDES))
        self.ball = Ball(self.options.angle, self.options.speed, self.players, self.court)

        self.playersprites = sprite.RenderPlain(self.players)
        self.ballsprite = sprite.RenderPlain(self.ball)
        self.allsprites = (self.ballsprite, self.playersprites)

    def post_init(self):
        pygame.event.set_allowed(self.ALLOWED_EVENTS)
        self.init_scores()
        
    def init_scores(self):
        self.scores = dict.fromkeys((0, 1), 0)
        self.scoreboard.draw()
            
    def update_scores(self, player):
        self.scores[player] += 1
        logger.debug("score : %s", self.scores)
        self.scoreboard.draw()
        
    def has_won(self, player):
        return (
            self.scores[player] >= 21
            and self.scores[player] - self.scores[not player] >= 2
            )
