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

from simplegame.events import EVNAMES, ALL_EVENTS

logger = logging.getLogger(os.path.basename(__file__))

# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# ---------------------------------------------------------------------------
# Helper functions and classes
# ---------------------------------------------------------------------------
def load_img(path):
    """ Load image from data directory and return
    a converted pygame image object and it's rect

    :param name: the name of the image file
    :return: a (:class:`pygame.image`, :class:`pygame:Rect`) tuple
    """
    try:
        image = pygame.image.load(path)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as e:
        logger.exception('Cannot load image:', fullname)
        raise
    return image, image.get_rect()

# ---------------------------------------------------------------------------
class GameProperty(object):
    def __init__(self, name, mode='r'):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return getattr(instance.game, self.name)

    def __set__(self, instance, value):
        if 'w' not in self.mode:
            raise AttributeError("Attribute %s is readonly" % self.name)
        setattr(instance, self.name, value)
        
            

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
        super(BaseSprite, self).__init__()
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
class Game(object):
    """ The main game object - mainly, a stack of game states.

    - initializes pygame, screen etc,
    - handles states stack and transitions
    - eventually act as mediator between states

    """
    
    INITIAL_STATE = NotImplemented
    SCREEN_SIZE = NotImplemented
    FPS = NotImplemented
    OPTIONS_DEFAULTS = {}
    STATES = ()

    # -----------------------------------------------------------------------
    def __init__(self, **options):
        self._options = None
        self._stack = [] ## A stack of game screens.
        self._states = {}
        self._state = None
        self._clock = None 
        self._screen = None
        self._fps = None

        self._init_options(options)
        
        self._init_pygame()
        self._init_clock()
        self._init_screen()
        self.before_init_states()
        self._init_states()
        self.on_init()
        
    # -----------------------------------------------------------------------
    # Housekeeping
    # -----------------------------------------------------------------------
    def _init_options(self, options):
        defaults = self.OPTIONS_DEFAULTS.copy()
        defaults.update(
            initial_state=self.INITIAL_STATE,
            screen_size=self.SCREEN_SIZE,
            fps=self.FPS
            )
        self.options = Options(options, defaults)
        
    def _init_pygame(self):
        pygame.init()

    def _init_clock(self):
        self._clock = pygame.time.Clock()
        self._fps = self.options.fps        

    def _init_screen(self):
        screen = self.getopt("screen", None)
        if screen is None:
            screen = pygame.display.set_mode(
                self.options.screen_size
                )
        self._screen = screen
        
    def _init_states(self):
        for statecls in self.STATES:
            self._states[statecls.NAME] = statecls(self)
        self.push(self._states[self.options.initial_state])
        
    # -----------------------------------------------------------------------
    # Options
    # -----------------------------------------------------------------------
    def getopt(self, name, default=None):
        return getattr(self.options, name, default)
    
    # -----------------------------------------------------------------------
    # States stack
    # -----------------------------------------------------------------------
    def get_state(self, name):
        return self._states.get(name)

    def push(self, state):
        logger.debug("push %s", state)
        self._stack.append(state)

    def pop(self):
        logger.debug("pop %s", self._stack[-1])
        return self._stack.pop()

    @property
    def empty(self):
        return not bool(self._stack)

    @property
    def state(self):
        return self._state

    def goto(self, statename):
        state = self.get_state(statename)
        self.push(state)

    # -----------------------------------------------------------------------
    # Clock & display & screen
    # -----------------------------------------------------------------------
    def tick(self, fps=None):
        fps = fps or self._fps
        self._clock.tick(fps)

    @property
    def display(self):
        return pygame.display

    @property
    def screen(self):
        return self._screen
    
    # -----------------------------------------------------------------------
    # Local events
    # -----------------------------------------------------------------------
    def before_init_states(self):
        """ Called just before `_init_states()`.

        If you have anything to do that states may depends on,
        do it here
        """
        
    def on_init(self):
        """ Called at the end of the `__init__`.
        Do any additional initialisation here.
        """
        pass
    
    def on_start(self):
        """ Called just before entering the main loop.

        Do any additional startup time stuff here
        """
        pass
    
    def on_exit(self):
        """ Called just before exiting the main loop.

        do any additional exit time stuff here """
        pass
    
    # -----------------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------------
    def run(self):
        #import pdb; pdb.set_trace()
        self.on_start()
        #import pdb; pdb.set_trace()
        while True:
            if self.empty:
                break ## Game over!
            
            self._state = self.pop()
            logger.debug("Main loop now switching to: %s", self._state)
            self._state.run(pygame.event)
            logger.debug("Returned to main loop from: %s", self._state)

        self.on_exit()

    def quit(self, state):
        logger.debug("quitting from state %s", state.NAME)
        self.on_exit()
        raise SystemExit()
        

# ---------------------------------------------------------------------------
class State(object):
    """ A game state.

    Handles the event loop, rendering, etc for a given game state.
    """
    NAME = NotImplemented
    FPS = None
    ALLOWED_EVENTS = ()
    
    # a State can be one of
    # - running
    # - suspended
    # - done

    def __init__(self, game):
        self.game = game
        self.fps = self.FPS or game.options.fps
        self.done = False
        self.on_init()
        
    def __str__(self):
        return self.NAME

    
    def on_init(self):
        """ Called at the end of the `__init__`.
        Do any additional initialisation here.
        """
        pass
    
    def on_start(self, resume=False):
        """ Called just before entering the main loop.

        Do any additional startup time stuff here.

        :param resume: if True, resuming from a previous call
        """
        pass
    
    def on_update(self):
        """ Do updates here """
        pass
        
    def on_render(self):
        """ Do the rendering here """
        pass

    def on_done(self):
        """ Do any additional cleaning here """
        pass


    def _block_queue(self, event_queue, clear=True):
        event_queue.set_allowed(None)
        if clear:
            event_queue.clear(ALL_EVENTS)
            
    def _unblock_queue(self, event_queue):
        event_queue.set_allowed(self._get_allowed_events())
        
    def _get_allowed_events(self):
        if self.ALLOWED_EVENTS:
            return self.ALLOWED_EVENTS
        if self.game.ALLOWED_EVENTS:
            return self.game.ALLOWED_EVENTS
        return ALL_EVENTS
    
    def _dispatch(self, event):
        if event.type >= USEREVENT:
            evname = "userevent"
        else:
            evname = EVNAMES.get(event.type, None)
            if not evname:
                logger.debug("Unknown event %s" % event)
                return
        hname = "on_%s" % evname.lower()
        handler = getattr(self, hname, None)
        if handler:
            logger.debug("calling handler %s for event %s : %s", hname, evname, event)
            handler(event)
                          
    def goto(self, next_state):
        self.game.goto(next_state)
        self.done = True

    def run(self, event_queue):
        self._block_queue(event_queue)
        resume = self.done
        self.done = False
        self.on_start(resume=resume)
        self._unblock_queue(event_queue)
        
        while not self.done:
            for event in event_queue.get():
                if event.type == QUIT:
                    self.game.quit(self)
                self._dispatch(event)

            # XXX pas sûr là
            if self.done:
                break
            
            self.on_update()
            self.on_render()
            self.game.display.flip()
            self.game.tick(self.fps)
        
        event_queue.clear()
        self.on_done()
        

    
