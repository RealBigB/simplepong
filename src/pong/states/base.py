# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

import pygame
from pygame.locals import * # XXX

from simplegame.base import State, StateProperty, GameProperty


# ---------------------------------------------------------------------------
class BaseStrategy(object):
    """ base class for sprite state-dependent behaviours """

    ball = StateProperty("ball")
    players = StateProperty("players")
    player1 = StateProperty("player1")
    player2 = StateProperty("player2")

    def __init__(self, state):
        self.state = state

    def reinit(self):
        pass

    def update(self):
        pass


# ---------------------------------------------------------------------------
class BallStrategy(BaseStrategy):
    """ base class for ball's state-dependant behaviours """

    @staticmethod
    def get_ball_rect_for_player(ball, player):
        p = player.rect
        b = ball.rect.copy()
        b.centerx = p.centerx
        b.midleft = p.midright
        return b

# ---------------------------------------------------------------------------
class NoopStrategy(BallStrategy):
    pass

# ---------------------------------------------------------------------------
class RunningState(State):
    """ Common 'running' game state stuff """
    screen = GameProperty("screen")
    court = GameProperty("court")
    ball = GameProperty("ball")
    players = GameProperty("players")
    playersprites = GameProperty("playersprites")
    ballsprite = GameProperty("ballsprite")
    allsprites = GameProperty("allsprites")

    BALL_STRATEGY = NoopStrategy
    
    @property
    def player1(self):
        return self.players[0]

    @property
    def player2(self):
        return self.players[1]

    def on_init(self):
        self.bgcolor = self.game.getopt("bgcolor", (0, 0, 0))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(self.bgcolor)
        self.ball_strategy = self.BALL_STRATEGY(self)
        
    def on_start(self, resume):
        pass

    def on_update(self):
        self.clearsprites()
        self.updatesprites()

    def on_render(self):
        self.drawsprites()

    def on_done(self):
        self.clearsprites()

    def clearsprites(self):
        for rect in self.ball.rect, self.player1.rect, self.player2.rect:
            self.screen.blit(self.background, rect, rect)

    def drawsprites(self):
        for sprite in self.allsprites:
            sprite.draw(self.screen)

    def updatesprites(self):
        for sprite in self.allsprites:
            sprite.update(self)

    def reinit_ball(self):
        self.ball_strategy.reinit()
    
    def update_ball(self):
        self.ball_strategy.update()

    
    def update_players(self):
        pass
    
