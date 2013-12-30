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

from simplegame import base
from simplegame.base import BaseSprite, GameProperty

logger = logging.getLogger(os.path.basename(__file__))

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

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

    image = os.path.join(DATA_DIR, "bat.png")
    
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

    image = os.path.join(DATA_DIR, "ball.png")
    
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
            self.last_hit_by = None
            # calculate new angle
            #self.angle = math.pi - self.angle

    def update(self, state=None, *args, **kw):
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
# The game states
# ---------------------------------------------------------------------------
# states are
# - intro : the introduction / instructions screen
# - playing : a party, from first service until one player wins

class Intro(base.State):
    NAME = 'intro'

# ---------------------------------------------------------------------------
class Party(base.State):
    NAME = 'party'
    
# ---------------------------------------------------------------------------
class Won(base.State):
    NAME = 'won'

    
# ---------------------------------------------------------------------------
class GameState(base.State):
    screen = GameProperty("screen")
    ball = GameProperty("ball")
    players = GameProperty("players")
    player1 = GameProperty("player1")
    player2 = GameProperty("player2")
    playersprites = GameProperty("playersprites")
    ballsprite = GameProperty("ballsprite")
    
    
    def on_init(self):
        self.bgcolor = self.game.getopt("bgcolor", (0, 0, 0))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(self.bgcolor)
        self.allsprites = (self.ballsprite, self.playersprites)

    def clearsprites(self):
        for rect in self.ball.rect, self.player1.rect, self.player2.rect:
            self.screen.blit(self.background, rect, rect)

    def drawsprites(self):
        for sprite in self.allsprites:
            sprite.draw(self.screen)

    def updatesprites(self):
        pass
    
    def on_update(self):
        self.clearsprites()
        self.updatesprites()

    def on_render(self):
        self.drawsprites()


# ---------------------------------------------------------------------------
class Service(GameState):
    NAME = 'service'

    def on_init(self):
        super(Service, self).on_init()
        font = pygame.font.Font(None, 36)
        # render(text, antialias, color, background=None) -> Surface
        # where background => bgcolor
        self.text = font.render("Press any key to start", True, (100, 100, 100))
        self.textrect = self.text.get_rect(centerx=self.background.get_width()/2)
        self.rendered = False
        
    def on_start(self, resume):
        self.clearsprites()
        self.ball.reinit()
        for player in self.players:
            player.reinit()
        self.rendered = False
        
        logger.debug("press any key to start")

    def on_keyup(self, event):
        self.game.goto("playing")
        self.done = True

    
    def on_render(self):
        if not self.rendered:
            self.screen.blit(self.text, self.textrect)
            self.rendered = True
        super(Service, self).on_render()

    def on_done(self):
        self.screen.blit(self.background, self.textrect, self.textrect)
        super(Service, self).on_done()

        
# ---------------------------------------------------------------------------
class Playing(GameState):
    NAME = 'playing'

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

    def on_done(self):
        # stop players from moving
        for player in self.players:
            player.still()
            
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
                

    def updatesprites(self):
        for sprite in self.allsprites:
            sprite.update(self)

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

# ---------------------------------------------------------------------------
# The scoreboard
# ---------------------------------------------------------------------------
class Score(object):
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
        self.scores = [Score(side, self.game.screen, self.background) for side in (0, 1)]
        
    screen = GameProperty("screen")

    def draw(self):
        for side, score in self.game.scores.items():
            self.scores[side].draw(score)
            
    def clear(self):
        for side in self.game.scores.keys():
            self.scores[side].clear()

# ---------------------------------------------------------------------------
# The game
# ---------------------------------------------------------------------------
class Pong(base.Game):
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
        self.players = tuple(Bat(side, player, self.screen) for player, side in enumerate(Bat.SIDES))
        self.ball = Ball(self.options.angle, self.options.speed, self.players, self.screen)
        self.playersprites = sprite.RenderPlain(self.players)
        self.ballsprite = sprite.RenderPlain(self.ball)
        self.scoreboard = ScoreBoard(self)

    def on_init(self):
        #import pdb; pdb.set_trace()
        # XXX marche pas ???
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
    
    @property
    def player1(self):
        return self.players[0]

    @property
    def player2(self):
        return self.players[1]

    
    # def new_ball(self):
    #     self.state = self.STATE_PENDING
    #     self.ball.reinit()
    #     for player in self.players:
    #         player.reinit()
    #     self.state = self.STATE_READY
    #     logger.debug("press any key to start")
    #     self.play()
        
    # def new_game(self):
    #     self._init_scores()
    #     self.new_ball()
        
    # def on_start(self):
    #     # Blit everything to the screen
    #     pygame.display.set_caption(self.caption)
    #     self.screen.blit(self.background, (0, 0))
    #     pygame.display.flip()

    # def play(self):

    #     # Initialise clock
    #     clock = pygame.time.Clock()

    #     self.paused = False
    #     # Event loop
    #     while True:
    #         # Make sure game doesn't run at more than 60 frames per second
    #         clock.tick(60)
    #         for event in pygame.event.get():
    #             if event.type == QUIT:
    #                 raise SystemExit
                
    #             if self.state != self.STATE_PLAYING:
    #                 if self.state == self.STATE_READY  and event.type == KEYUP:
    #                     self.state = self.STATE_PLAYING
    #                 continue
                
    #             if self.state == self.STATE_PLAYING:
    #                 if event.type == OFFCOURT:
    #                     logger.debug("OUT")
    #                     player = event.last_hit_by
    #                     if player:
    #                         self.update_scores(player.player)
    #                         self.display_scores()
    #                         if self.has_won(player.player):
    #                             logger.debug("player %s won", player)
    #                             self.new_game()
    #                             return
    #                         self.new_ball()
    #                         continue
                        
    #                 if self.set_paused(event):
    #                     continue
                    
    #                 self.dispatch(event)
            
                
    #         self.screen.blit(self.background, self.ball.rect, self.ball.rect)
    #         self.screen.blit(self.background, self.player1.rect, self.player1.rect)
    #         self.screen.blit(self.background, self.player2.rect, self.player2.rect)
            
    #         # for sprite in (self.ball, self.player1, self.player2):
    #         #     # XXX make blit a method of the groups ???
    #         #     self.screen.blit(self.background, sprite.rect, sprite.rect)

    #         if self.state == self.STATE_PLAYING and not self.paused:
    #             # XXX why 2 groups ????
    #             self.ballsprite.update()
    #             self.playersprites.update()

    #         self.ballsprite.draw(self.screen)
    #         self.playersprites.draw(self.screen)
    #         pygame.display.flip()
