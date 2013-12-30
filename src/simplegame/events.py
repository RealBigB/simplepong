# -*- coding: utf-8 -*-
# from http://www.pygame.org/docs/ref/event.html#comment_pygame_event_Event comments
from pygame.locals import *

EVNAMES = {                                 # from SDL-1.2.14\include\SDL_events.h
    NOEVENT: 'NOEVENT',                      #  0  SDL_NOEVENT
    ACTIVEEVENT: 'ACTIVEEVENT',              #  1  SDL_ACTIVEEVENT
    KEYDOWN: 'KEYDOWN',                      #  2  SDL_KEYDOWN
    KEYUP: 'KEYUP',                          #  3  SDL_KEYUP
    MOUSEMOTION: 'MOUSEMOTION',              #  4  SDL_MOUSEMOTION
    MOUSEBUTTONDOWN: 'MOUSEBUTTONDOWN',      #  5  SDL_MOUSEBUTTONDOWN
    MOUSEBUTTONUP: 'MOUSEBUTTONUP',          #  6  SDL_MOUSEBUTTONUP
    JOYAXISMOTION: 'JOYAXISMOTION',          #  7  SDL_JOYAXISMOTION
    JOYBALLMOTION: 'JOYBALLMOTION',          #  8  SDL_JOYBALLMOTION
    JOYHATMOTION: 'JOYHATMOTION',            #  9  SDL_JOYHATMOTION
    JOYBUTTONDOWN: 'JOYBUTTONDOWN',          # 10  SDL_JOYBUTTONDOWN
    JOYBUTTONUP: 'JOYBUTTONUP',              # 11  SDL_JOYBUTTONUP
    QUIT: 'QUIT',                            # 12  SDL_QUIT
    SYSWMEVENT: 'SYSWMEVENT',                # 13  SDL_SYSWMEVENT
                                             # 14  SDL_EVENT_RESERVEDA
                                             # 15  SDL_EVENT_RESERVEDB
    VIDEORESIZE: 'VIDEORESIZE',              # 16  SDL_VIDEORESIZE
    VIDEOEXPOSE: 'VIDEOEXPOSE' ,             # 17  SDL_VIDEOEXPOSE
                                             # 18  SDL_EVENT_RESERVED2
                                             # 19  SDL_EVENT_RESERVED3
                                             # 20  SDL_EVENT_RESERVED4
                                             # 21  SDL_EVENT_RESERVED5
                                             # 22  SDL_EVENT_RESERVED6
                                             # 23  SDL_EVENT_RESERVED7
    USEREVENT: 'USEREVENT',                  # 24  SDL_USEREVENT
    NUMEVENTS: 'NUMEVENTS',                  # 32  SDL_NUMEVENTS
}

ALL_EVENTS = range(NOEVENT, NUMEVENTS)

def event_name(evtype):
    '''return a displayable name for a pygame/SDL event type number'''
    try:
        result = _EVNAMES[evtype]
    except:
        if evtype in range(USEREVENT,NUMEVENTS):
            result = 'USEREVENT+' + repr(evtype-USEREVENT)
        elif evtype >= NUMEVENTS:
            result = 'ILLEGAL_EVENT_' + repr(evtype)
        elif evtype == 14:
            result = 'EVENT_RESERVEDA'
        elif evtype == 15:
            result = 'EVENT_RESERVEDB'
        else:
            result = 'EVENT_RESERVED' + repr(evtype-16)
    return result

