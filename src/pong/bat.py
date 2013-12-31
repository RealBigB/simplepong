# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

from pong.base import ImageSprite


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

    image = "bat.png"
    
    def __init__(self, side, player, area):
        super(Bat, self).__init__(area)
        
        self.side = side
        self.player = player
        self.speed = 10
        self.state = self.STATE_STILL
        self.movepos = [0,0]
        self.init_position()

    def __str__(self):
        return "player%s" % (self.player + 1)
    
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

    def init_position(self):
        if self.side == self.SIDE_LEFT:
            self.rect.midleft = self.area.midleft
        elif self.side == self.SIDE_RIGHT:
            self.rect.midright = self.area.midright

    def reinit(self, state):
        self.init_position()
    
    def update(self, state, *args, **kw):
        """ XXX """
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos

