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

from simplegame.base import GameProperty
from simplegame.sprites import ImageSprite

from pong.events import BallOffCourt

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Game objects
# ---------------------------------------------------------------------------
class Bat(ImageSprite):
    """ A movable tennis bat with which one hits the ball

    XXX Document me

    :attr side: XXX
    :att speed: how many pixels does the bat moves when it moves
    :attr state: is the bat moving, and if yes is it moving up or down
    :attr movepos: 
    """

    SIDE_LEFT = "left"
    SIDE_RIGHT = "right"
    SIDES = (SIDE_LEFT, SIDE_RIGHT)
    
    STATE_STILL = "still"
    STATE_MOVEUP = "moveup"
    STATE_MOVEDOWN = "movedown"

    image = os.path.join(DATA_DIR, "bat.png")
    
    def __init__(self, side, player, area):
        super(Bat, self).__init__(self.image, area)
        
        self.side = side
        self.player = player
        self.speed = 10
        self.state = self.STATE_STILL
        self.movepos = [0,0]
        self.reinit()

    def __str__(self):
        return "player%s" % (self.player + 1)
    
    def update(self, state=None, *args, **kw):
        """ XXX """
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos

    def moveup(self):
        """ XXX """
        self.movepos[1] = self.movepos[1] - (self.speed)
        self.state = self.STATE_MOVEUP

    def movedown(self):
        """ XXX """
        self.movepos[1] = self.movepos[1] + (self.speed)
        self.state = self.STATE_MOVEDOWN

    def still(self):
        self.movepos = [0,0]
        self.state = self.STATE_STILL

    def reinit(self):
        """ Resets the bat's state to initial state. """
        if self.side == self.SIDE_LEFT:
            self.rect.midleft = self.area.midleft
        elif self.side == self.SIDE_RIGHT:
            self.rect.midright = self.area.midright

    
# ---------------------------------------------------------------------------
class Ball(ImageSprite):
    """ A ball that will move across the screen.

    :param vector: an (angle, speed) tuple
    :param player1: XXX
    :param player2: XXX
    
    :attr vector: an (angle, speed) tuple
    :attr hit: boolen flag, has the ball been hit by a player
    """

    image = os.path.join(DATA_DIR, "ball.png")

    def __init__(self, angle, speed, players, area):
        super(Ball, self).__init__(self.image, area)
        self._initstate = (angle, speed)
        self.angle = angle
        self.speed = speed
        self.hit = False
        self.last_hit_by = None
        self.players = players
        

    def on_state_change(self, newstate):
        self.strategy = newstate.get_strategy_for("ball")
        
    def reinit(self):
        self.angle, self.speed = self._initstate
        #self.rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self.rect = self.strategy.get_ball_rect_for_player(self, self.players[0])
        
        
    def update(self, state=None, *args, **kw):
        """ """
        self.strategy.update()


# ---------------------------------------------------------------------------
class ServiceText(object):
    def __init__(self, message, screen, background):
        self.message = message
        self.screen = screen
        self.background = background
        font = pygame.font.Font(None, 36)
        # render(text, antialias, color, background=None) -> Surface
        # where background => bgcolor
        self.text = font.render(self.message, True, (100, 100, 100))
        self.textrect = self.text.get_rect(centerx=self.background.get_width()/2)
        self.rendered = False

    def draw(self):
        if not self.rendered:
            self.screen.blit(self.text, self.textrect)
            self.rendered = True

    def clear(self):
        self.screen.blit(self.background, self.textrect, self.textrect)
        

# ---------------------------------------------------------------------------
# The scoreboard
# ---------------------------------------------------------------------------
class ScoreWidget(object):
    SIDE_LEFT = 0
    SIDE_RIGHT = 1

    def __init__(self, side, screen, background):
        self.side = side
        self.screen = screen
        self.background = background
        self.font = pygame.font.Font(None, 20)
        self.labeltext = "Player %s : %%02d" % (self.side + 1)
        self.y = (self.background.get_size()[1] - self.font.size(self.labeltext)[1])  - 20
        self.x = (30, self.background.get_size()[0] - self.font.size(self.labeltext)[0] - 20)[self.side]
        self.text = None
        self.rect = None
        self.draw(0)
        
    def draw(self, score):
        self.clear()
        self.text = self.font.render(self.labeltext % score, True, (255, 255, 255))
        self.rect = self.text.get_rect(topleft=(self.x, self.y))
        self.screen.blit(self.text, self.rect)

    def clear(self):
        if self.text:
            self.screen.blit(self.background, self.rect, self.rect)
        

class ScoreBoard(object):
    def __init__(self, game):
        self.game = game
        self.bgcolor = self.game.getopt("bgcolor", (0, 0, 0))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(self.bgcolor)
        self.scores = [ScoreWidget(side, self.game.screen, self.background) for side in (0, 1)]
        
    screen = GameProperty("screen")

    def draw(self):
        for side, score in self.game.scores.items():
            self.scores[side].draw(score)
            
    def clear(self):
        for side in self.game.scores.keys():
            self.scores[side].clear()
