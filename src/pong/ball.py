# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

from pong.base import ImageSprite


class Ball(ImageSprite):
    """ A ball that will move across the screen.

    :param vector: an (angle, speed) tuple
    :param player1: XXX
    :param player2: XXX

    # XXX fix me
    :attr vector: an (angle, speed) tuple
    :attr hit: boolen flag, has the ball been hit by a player
    """

    image = "ball.png"

    def __init__(self, angle, speed, players, area):
        super(Ball, self).__init__(area)
        self._initstate = (angle, speed)
        self.angle = angle
        self.speed = speed
        self.hit = False
        self.last_hit_by = None
        self.players = players
        
    def reinit(self, state):
        self.angle, self.speed = self._initstate
        state.reinit_ball()
        
    def update(self, state=None, *args, **kw):
        """ """
        state.update_ball()

