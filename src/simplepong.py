# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
import os
import sys
import random
import math

import pygame
from pygame.locals import * # XXX
from pygame import sprite

from simplepong.base import BaseSprite

logger = logging.getLogger(os.path.basename(__file__))

# ---------------------------------------------------------------------------
# Custom events
# ---------------------------------------------------------------------------
OFFCOURT = USEREVENT + 1 # what's wrong with 42 ?
def BallOffCourt(side, last_hit_by):
    return pygame.event.Event(OFFCOURT, side=side, last_hit_by=last_hit_by)

# ---------------------------------------------------------------------------
# Game objects
# ---------------------------------------------------------------------------
class Bat(BaseSprite):
    """ A movable tennis 'bat' with which one hits the ball

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
    
    def __init__(self, side, player, screen=None):
        super(Bat, self).__init__(self.image, screen)
        
        self.side = side
        self.player = player
        self.speed = 10
        self.state = self.STATE_STILL
        self.movepos = [0,0]
        self.reinit()

    def __str__(self):
        return "player%s" % (self.player + 1)
    
    def update(self):
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
        """ Resets the bat's state to initial state.
        """
        if self.side == self.SIDE_LEFT:
            self.rect.midleft = self.area.midleft
        elif self.side == self.SIDE_RIGHT:
            self.rect.midright = self.area.midright

# ---------------------------------------------------------------------------        
class Ball(BaseSprite):
    """ A ball that will move across the screen.

    :param vector: an (angle, speed) tuple
    :param player1: XXX
    :param player2: XXX
    
    :attr vector: an (angle, speed) tuple
    :attr hit: boolen flag, has the ball been hit by a player
    """

    image = "ball.png"
    
    def __init__(self, angle, speed, players, screen=None):
        super(Ball, self).__init__(self.image, screen)
        self._initstate = (angle, speed)
        self.angle = angle
        self.speed = speed
        self.hit = False
        self.last_hit_by = None
        self.players = players

    def reinit(self):
        self.angle, self.speed = self._initstate
        self.rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        
    # XXX do we use this, really ?
    @property
    def vector(self):
        return self.angle, self.speed

    @vector.setter
    def vector(self, vector):
        self.angle, self.speed = vector

    def _check_hit(self):
        if not self.area.contains(self.rect):
            return False
        
        # Deflate the rectangles so you can't catch a ball behind the bat
        for player in self.players:
            player.rect.inflate(-3, -3)

        # Do ball and bat collide?
        # Note I put in an odd rule that sets self.hit to 1 when they collide, and unsets it in the next
        # iteration. this is to stop odd ball behaviour where it finds a collision *inside* the
        # bat, the ball reverses, and is still inside the bat, so bounces around inside.
        # This way, the ball can always escape and bounce away cleanly
        if self.hit:
            self.hit = False
        else:
            for player in self.players:
                if self.rect.colliderect(player.rect) == 1:
                    logger.debug("ball hit by player %s", player)
                    self.hit = True
                    self.last_hit_by = player
                    # calculate new angle
                    self.angle = math.pi - self.angle
                    break
                
        return True
            
    def _check_out(self):
        if self.area.contains(self.rect):
            return False
        
        # area (is supposed to) contain the ball,
        # so area.collidepoint(self.rect.XXX) will return True
        # as long as the ball is within the area.
        # What we want here is to detect if the ball is
        # outside the area - or, more exactly, on which
        # side of the area it got out.

        # tl : rect.topleft is outside the area
        tl = not self.area.collidepoint(self.rect.topleft)
        # tr : rect.topright is outside the area
        tr = not self.area.collidepoint(self.rect.topright)
        # bl : rect.bottomleft is outside the area
        bl = not self.area.collidepoint(self.rect.bottomleft)
        # br : rect.bottomrigh is outside the area
        br = not self.area.collidepoint(self.rect.bottomright)

        hit_top = (tr and tl)
        hit_bottom = (br and bl)
        out_left = tl and bl
        out_right = tr and br

        if hit_top or hit_bottom:
            # calculate new angle
            self.angle = - self.angle

        if out_left or out_right:
            logger.debug("going out %s ", ("left", "right")[out_right])
            # XXX debug
            # if out_left:
            #     self.angle = math.pi - self.angle
            #     return
            
            side = (0, 1)[out_right]
            evt = BallOffCourt(side, self.last_hit_by) 
            pygame.event.post(evt)

            # self.offcourt()
            # calculate new angle
            #self.angle = math.pi - self.angle

    def update(self):
        """ """
        newpos = self.getnewpos(*self.vector)
        self.rect = self.rect.move(newpos)
        if not self._check_hit():
            self._check_out()

    def getnewpos(self, angle, speed):
        """ calculate a new position according to (angle, speed).

        cf http://www.pygame.org/docs/tut/tom/games4.html chapter 4.1.2
        
        :param angle: XXX
        :param speed: XXX
        :return: a (dx, dy) tuple for the next position
        """
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        return dx, dy



# ---------------------------------------------------------------------------
# The game itself
# ---------------------------------------------------------------------------
class ParamGetter(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return instance._params[self.name]
    def __set__(self, instance, value):
        raise AttributeError("Attribute %s is read-only" % self.name)
    
# ---------------------------------------------------------------------------
class Pong(object):
    _defaults = {
        "size": (640, 480),
        "bgcolor" : (0, 0, 0),
        "speed" : 13,
        "angle": 0.47,
        "caption": "Basic Pong",
        # A suivre
        }

    size = ParamGetter("size")
    bgcolor = ParamGetter("bgcolor")
    speed = ParamGetter("speed")
    angle = ParamGetter("angle")
    caption = ParamGetter("caption")

    STATE_PENDING = "pending"
    STATE_READY = "ready"
    STATE_PLAYING = "playing"
    
    def __init__(self, **kw):
        pygame.init()

        self._params = dict((k, kw.pop(k, default)) for k, default in self._defaults.iteritems())
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(self.bgcolor)

        self.players = tuple(Bat(side, player, self.screen) for player, side in enumerate(Bat.SIDES))
        self.ball = Ball(self.angle, self.speed, self.players, self.screen)

        self.playersprites = sprite.RenderPlain(self.players)
        self.ballsprite = sprite.RenderPlain(self.ball)

        self._init_scores()
        self.state = None
        

    def _init_scores(self):
        self.scores = dict.fromkeys((0, 1), 0)
            
    def update_scores(self, player):
        self.scores[player] += 1
        
    @property
    def player1(self):
        return self.players[0]

    @property
    def player2(self):
        return self.players[1]

    def set_paused(self, event):
        if event.type == KEYUP and event.key == K_SPACE:
            self.paused = not self.paused
            logger.debug("PAUSE : %s", ("out", "in")[self.paused])
        return self.paused
        
    def dispatch(self, event):
        # XXX quelque chose de plus élégant ?
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.player1.moveup()
            elif event.key == K_q:
                self.player1.movedown()
            elif event.key == K_UP:
                self.player2.moveup()
            elif event.key == K_DOWN:
                self.player2.movedown()

        elif event.type == KEYUP:
            if event.key == K_a or event.key == K_q:
                self.player1.still()
            elif event.key == K_UP or event.key == K_DOWN:
                self.player2.still()

    def run(self):
        self.new_game()

    def new_ball(self):
        self.state = self.STATE_PENDING
        self.ball.reinit()
        for player in self.players:
            player.reinit()
        self.state = self.STATE_READY
        logger.debug("press any key to start")
        self.play()
        
    def new_game(self):
        self._init_scores()
        self.new_ball()
        
    def display_scores(self):
        logger.debug("scores : %s", self.scores)

    def update_scores(self, player):
        self.scores[player] += 1
    
    def has_won(self, player):
        return (
            self.scores[player] >= 21
            and self.scores[player] - self.scores[not player] >= 2
            )

    def play(self):
        # Blit everything to the screen
        pygame.display.set_caption(self.caption)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        # Initialise clock
        clock = pygame.time.Clock()

        self.paused = False
        # Event loop
        while True:
            # Make sure game doesn't run at more than 60 frames per second
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    raise SystemExit
                
                if self.state != self.STATE_PLAYING:
                    if self.state == self.STATE_READY  and event.type == KEYUP:
                        self.state = self.STATE_PLAYING
                    continue
                
                if self.state == self.STATE_PLAYING:
                    if event.type == OFFCOURT:
                        logger.debug("OUT")
                        player = event.last_hit_by
                        if player:
                            self.update_scores(player.player)
                            self.display_scores()
                            if self.has_won(player.player):
                                logger.debug("player %s won", player)
                                self.new_game()
                                return
                            self.new_ball()
                            continue
                        
                    if self.set_paused(event):
                        continue
                    
                    self.dispatch(event)
            
                
            self.screen.blit(self.background, self.ball.rect, self.ball.rect)
            self.screen.blit(self.background, self.player1.rect, self.player1.rect)
            self.screen.blit(self.background, self.player2.rect, self.player2.rect)
            
            # for sprite in (self.ball, self.player1, self.player2):
            #     # XXX make blit a method of the groups ???
            #     self.screen.blit(self.background, sprite.rect, sprite.rect)

            if self.state == self.STATE_PLAYING and not self.paused:
                # XXX why 2 groups ????
                self.ballsprite.update()
                self.playersprites.update()

            self.ballsprite.draw(self.screen)
            self.playersprites.draw(self.screen)
            pygame.display.flip()
