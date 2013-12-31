# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
#import os
#import sys
#import getopt
#import logging
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from pong.game import Pong

def main():
    game = Pong()
    game.run()

if __name__ == "__main__":
    main()

__all__ = ("Pong", "main")


    
