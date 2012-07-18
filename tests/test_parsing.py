#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.Syntax import Syntax

class RulesTestCase(unittest.TestCase):
    
    def test_basic(self):
        """Just apply rules
        """
        syntax = Syntax('debiancontrol.xml')
        self.assertEqual(syntax.parseBlockTextualResults('Section:'),
                         [('INIT', 8, [('RegExpr([^ ]*:)', 0, 8)])])
        self.assertEqual(syntax.parseBlockTextualResults(' '),
                         [('INIT', 1, [('DetectChar( )', 0, 1)])])
        self.assertEqual(syntax.parseBlockTextualResults('Provides:'),
                         [('INIT', 9, [('StringDetect(Provides:)', 0, 9)])])
    
    def test_rule_switches_context(self):
        """Matched rule switches context
        """
        syntax = Syntax('debiancontrol.xml')
        self.assertEqual(syntax.parseBlockTextualResults('Section: editors'),
                         [('INIT', 8, [('RegExpr([^ ]*:)', 0, 8)]), ('Field', 8, [])])
        self.assertEqual(syntax.parseBlockTextualResults(' Section: editors'),
                         [('INIT', 1, [('DetectChar( )', 0, 1)]), ('Field', 16, [])])
        self.assertEqual(syntax.parseBlockTextualResults('Provides: xxx'),
                         [('INIT', 9, [('StringDetect(Provides:)', 0, 9)]), ('DependencyField', 4, [])])

if __name__ == '__main__':
    unittest.main()
