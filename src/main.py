# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import pong

if __name__ == "__main__":
    pong.main()
