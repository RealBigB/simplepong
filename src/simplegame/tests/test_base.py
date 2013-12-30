# -*- coding: utf-8 -*-
""" Simple pygame tutorial
cf http://www.pygame.org/docs/tut/tom/
"""
import os, sys
# kludge
_HERE = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.sep.join(_HERE.split(os.path.sep)[:-2])
sys.path.append(_ROOT)

import logging
import unittest
from simplegame import base

class TestOptions(unittest.TestCase):
    def test_attribute_lookup_raises_attributeerror_if_no_matching_option(self):
        options = base.Options({})
        self.assertRaises(AttributeError, getattr, options, "yadda")

    def test_attribute_lookup_returns_default_if_matching_default_and_no_matching_option(self):
        options = base.Options({}, dict(yadda=42))
        self.assertEqual(42, options.yadda)
        
    def test_attribute_lookup_returns_option_if_matching__option(self):
        options = base.Options(dict(yadda=1764), dict(yadda=42))
        self.assertEqual(1764, options.yadda)


class GameMock(object):
    def __init__(self, *args, **kw):
        pass

class TestState(unittest.TestCase):
    pass

class TestGame(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
