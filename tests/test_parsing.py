#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.Syntax import Syntax

class RulesTestCase(unittest.TestCase):
    
    def test_basic(self):
        syntax = Syntax('debiancontrol.xml')
        self.assertEqual(syntax.parseBlockTextualResults('Section: editors'),
                         [('INIT', 16, [('RegExpr([^ ]*:)', 0, 8)])])
        self.assertEqual(syntax.parseBlockTextualResults(' Section: editors'),
                         [('INIT', 17, [('DetectChar( )', 0, 1)])])
        self.assertEqual(syntax.parseBlockTextualResults('Provides: xxx'),
                         [('INIT', 13, [('StringDetect(Provides:)', 0, 9)])])


if __name__ == '__main__':
    unittest.main()
