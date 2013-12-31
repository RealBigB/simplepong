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
from pong.states.base import BallStrategy, RunningState


# ---------------------------------------------------------------------------
class PlayingStrategy(BallStrategy):
    def __init__(self, state):
        super(PlayingStrategy, self).__init__(state)
        
    def update(self, state=None, *args, **kw):
        """ """
        newpos = self.getnewpos(self.ball.angle, self.ball.speed)
        self.ball.rect = self.ball.rect.move(newpos)
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
    
    def _check_hit(self):
        if not self.ball.area.contains(self.ball.rect):
            return False
        
        # Deflate the rectangles so you can't catch a ball behind the bat
        for player in self.players:
            player.rect.inflate(-3, -3)

        # Do ball and bat collide?
        # Note I put in an odd rule that sets self.hit to 1 when they collide, and unsets it in the next
        # iteration. this is to stop odd ball behaviour where it finds a collision *inside* the
        # bat, the ball reverses, and is still inside the bat, so bounces around inside.
        # This way, the ball can always escape and bounce away cleanly
        if self.ball.hit:
            self.ball.hit = False
        else:
            for player in self.players:
                if self.ball.rect.colliderect(player.rect) == 1:
                    logger.debug("ball hit by player %s", player)
                    self.ball.hit = True
                    self.ball.last_hit_by = player
                    # calculate new angle
                    self.ball.angle = math.pi - self.ball.angle
                    break
                
        return True
            
    def _check_out(self):
        area = self.ball.area
        rect = self.ball.rect
        
        if area.contains(rect):
            return False
        
        # area (is supposed to) contain the ball,
        # so area.collidepoint(self.rect.XXX) will return True
        # as long as the ball is within the area.
        # What we want here is to detect if the ball is
        # outside the area - or, more exactly, on which
        # side of the area it got out.

        # tl : rect.topleft is outside the area
        tl = not area.collidepoint(rect.topleft)
        # tr : rect.topright is outside the area
        tr = not area.collidepoint(rect.topright)
        # bl : rect.bottomleft is outside the area
        bl = not area.collidepoint(rect.bottomleft)
        # br : rect.bottomrigh is outside the area
        br = not area.collidepoint(rect.bottomright)

        hit_top = (tr and tl)
        hit_bottom = (br and bl)
        out_left = tl and bl
        out_right = tr and br

        if hit_top or hit_bottom:
            # calculate new angle
            self.ball.angle = - self.ball.angle

        if out_left or out_right:
            logger.debug("going out %s ", ("left", "right")[out_right])
            # XXX debug
            # if out_left:
            #     self.angle = math.pi - self.angle
            #     return
            
            side = (0, 1)[out_right]
            evt = BallOffCourt(side, self.ball.last_hit_by) 
            pygame.event.post(evt)
            self.ball.last_hit_by = None
            # calculate new angle
            #self.angle = math.pi - self.angle


# ---------------------------------------------------------------------------
class Playing(RunningState):
    NAME = 'playing'

    BALL_STRATEGY = PlayingStrategy
    
    def on_start(self, resume):
        super(Playing, self).on_start(resume)
        self.ball.reinit(self) # XXX
        # for player in self.players:
        #     player.reinit(self)

    def on_done(self):
        # stop players from moving
        self.clearsprites()
        for player in self.players:
            player.still()

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
            logger.debug("Playing -> pause")
            self.goto("paused")
        
        elif event.key == K_a or event.key == K_q:
            self.player1.still()
        elif event.key == K_UP or event.key == K_DOWN:
            self.player2.still()

    def on_userevent(self, event):
        if event.type == OFFCOURT:
            logger.debug("OUT")
            player = event.last_hit_by
            if player:
                self.game.update_scores(player.player)
                if self.game.has_won(player.player):
                    logger.debug("player %s won", player)
                    self.goto("won")
                else:
                    self.goto("service")
            else:
                # aucun des deux n'a touché la balle
                # à terme ça ne devrait pas arriver
                # puisque c'est un des joueurs qui aura le
                # service, mais pour le moment...
                logger.debug("oops, quels maladroits")
                self.goto("service")
                
            
    def update_ball(self):
        PlayingStrategy(self).update()


