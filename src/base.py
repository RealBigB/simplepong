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


logger = logging.getLogger(os.path.basename(__file__))

# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# ---------------------------------------------------------------------------
# Helper functions and classes
# ---------------------------------------------------------------------------
def load_img(name):
    """ Load image from data directory and return
    a converted pygame image object and it's rect

    :param name: the name of the image file
    :return: a (:class:`pygame.image`, :class:`pygame:Rect`) tuple
    """
    fullname = os.path.join(DATA_DIR, name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as e:
        logger.exception('Cannot load image:', fullname)
        raise
    return image, image.get_rect()

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
# Base game classes
# ---------------------------------------------------------------------------
class BaseSprite(sprite.Sprite):
    """ Abstract base class, factors out common parts of our game objects

    :param image_name: the name of the image to load for thsi child class
    
    :attr image: a :class:`pygame.image` instance
    :attr rect: a :class:`pygame.rect` for the :attr:`image`
    :attr area: the :class:`pygame.Rect` for the main screen or None
    """
    def __init__(self, image_name, screen=None):
        super(ImgRectSprite, self).__init__()
        self.image, self.rect = load_img(image_name)
        if screen is None:
            screen = pygame.display.get_surface()
        self.area = screen.get_rect()



# ---------------------------------------------------------------------------
class Options(object):
    def __init__(self, options, defaults=None):
        self._options = options
        self._defaults = defaults or {}

    def __getattr__(self, name):
        for container in self._options, self._defaults:
            if name in container:
                return container[name]
        raise AttributeError("No option named %s" % name)
     
# ---------------------------------------------------------------------------
class BaseGame(object):
    """ The main game object - mainly, a stack of game states.

    - initializes pygame, screen etc,
    - handles states stack and transitions
    - eventually act as mediator between states
    """
    
    INITITAL_STATE = NotImplemented
    SCREEN_SIZE = NotImplemented
    FPS = NotImplemented
    OPTIONS_DEFAULTS = None
    STATES = {}
    
    # -----------------------------------------------------------------------
    def __init__(self, **options):
        self.options = Options(options, self.OPTIONS_DEFAULTS)
        self._stack = [] ## A stack of game screens.
        self._states = {}
        self._state = None
        self._clock = None 
        self._screen = None
        self._fps = None
        self._init_pygame()
        self._init_clock()
        self._init_screen()
        self._init_states()
    
    # -----------------------------------------------------------------------
    # Housekeeping
    # -----------------------------------------------------------------------
    def _init_pygame(self):
        pygame.init()

    def _init_clock(self):
        self._clock = pygame.time.Clock()
        self._fps = self.getopt("fps", self.FPS)        

    def _init_screen(self):
        screen = self.getopt("screen", None)
        if screen is None:
            screen = pygame.display.set_mode(
                self.getopt("screen_size", self.SCREEN_SIZE)
                )
        self._screen = screen
        
    def _init_states(self):
        for statename, statecls in self.STATES:
            self._states[statename] = statecls(self)
        self._push(self._states[self.INITITAL_STATE])
        
    # -----------------------------------------------------------------------
    # Options
    # -----------------------------------------------------------------------
    def getopt(self, name, default=None):
        return self.options.get(name, default)
    
    # -----------------------------------------------------------------------
    # States stack
    # -----------------------------------------------------------------------
    def _get_state(self, name):
        return self._states.get(name)

    def _push(self, state):
        self._stack.push(state)

    def _pop(self):
        return self._stack.pop()

    @property
    def _empty(self):
        return bool(self._stack)

    @property
    def current_state(self):
        return self._state

    def goto(self, statename):
        state = self._get_state(statename)
        self._push(state)

    # -----------------------------------------------------------------------
    # Clock
    # -----------------------------------------------------------------------
    def tick(self, fps=None):
        fps = fps or self._fps
        self._clock.tick(fps)
        
    # -----------------------------------------------------------------------
    # Local events
    # -----------------------------------------------------------------------
    def on_start(self):
        """ do any additional startup time stuff here """
        pass
    
    def on_exit(self):
        """ do any additional exit time stuff here """
        pass
    
    # -----------------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------------
    def run(self):
        self.on_start()
        while True:
            if self._empty:
                break ## Game over!
            
            self._state = self.pop()
            logger.debug("Returned to main loop. Now switching to: %s", self._state)
            self._state.run()

        self.on_exit()
        

# ---------------------------------------------------------------------------
class BaseState(object):
    """ A game state.

    Handles the event loop, rendering, etc for a given game state.
    """
    NAME = NotImplemented
    
    def __init__(self, game):
        self.game = game
        self.done = False
        
    def on_start(self):
        """ Do any additional initialisation here """
        pass

    def on_done(self):
        """ Do any additional cleaning here """
        pass

    def render(self):
        """ Do the rendering here """

    def _dispatch(event):
        handler = getattr(self, "on_%s" % event.type, None)
        if handler:
            handler(event)
                          
    def goto(self, next_state):
        self.done = True
        self.game.goto(next_state)

    def run(self):
        self._run()
        
    def _run(self):
        self.on_start()
        while not self.done:
            for event in pygame.event.get():
                self._dispatch(event)

            if self.done:
                break

            self.render()
            self.game.tick()
        
        self.on_done()
        

    
