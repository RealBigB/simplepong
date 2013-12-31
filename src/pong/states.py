# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
import random
import math

import pygame
from pygame import sprite
from pygame.locals import * # XXX

from simplegame.base import State, DelegateProperty, GameProperty

from pong.events import BallOffCourt, OFFCOURT
from pong.objects import ServiceText


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
def StateProperty(attr, mode="r"):
    return DelegateProperty("state", attr, mode)

class BallStrategy(object):
    def __init__(self, state):
        self.state = state

    ball = StateProperty("ball")
    players = StateProperty("players")
    player1 = StateProperty("player1")
    player2 = StateProperty("player2")

    @staticmethod
    def get_ball_rect_for_player(ball, player):
        p = player.rect
        b = ball.rect.copy()
        b.centerx = p.centerx
        b.midleft = p.midright
        return b

    def update(self):
        pass

    def reinit(self):
        pass
    
class NoopStrategy(BallStrategy):
    pass

    
class ServiceStrategy(BallStrategy):
    """ A ball sticking to a :class:Bat` """

    def __init__(self, state):
        super(ServiceStrategy, self).__init__(state)

    def reinit(self):
        self.ball.rect = self.get_ball_rect_for_player(self.ball, self.player1)
        self.ball.last_hit_by = self.player1
        
    def update(self, *args, **kw):
        self.ball.rect = self.get_ball_rect_for_player(self.ball, self.player1)
        
        

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
# The game states
# ---------------------------------------------------------------------------
# states are
# - intro : the introduction / instructions screen
# - playing : a party, from first service until one player wins

class Intro(State):
    NAME = 'intro'

# ---------------------------------------------------------------------------
class Party(State):
    NAME = 'party'
    
# ---------------------------------------------------------------------------
class Won(State):
    NAME = 'won'

    
# ---------------------------------------------------------------------------
class GameState(State):
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
    
# ---------------------------------------------------------------------------
class Service(GameState):
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


        
# ---------------------------------------------------------------------------
class Playing(GameState):
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



# ---------------------------------------------------------------------------
class Paused(GameState):
    NAME = 'paused'

    def on_keyup(self, event):
        if event.key == K_SPACE:
            logger.debug("Pause -> playing")
            self.game.goto("playing")
            self.done = True

    def updatespites(self):
        pass
