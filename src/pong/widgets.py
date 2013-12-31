# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import logging
logger = logging.getLogger(__name__)

import pygame

from simplegame.base import GameProperty


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
        

# ---------------------------------------------------------------------------
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
