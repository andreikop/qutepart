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

    def test_pop_context(self):
        """Checks if #pop operation works correctly
        """
        syntax = Syntax('debiancontrol.xml')

        self.assertEqual(syntax.parseBlockTextualResults(' ${a} ${b}'),
                         [('INIT', 1, [('DetectChar( )', 0, 1)]), 
                          ('Field', 2, [('Detect2Chars(${)', 1, 2)]),
                          ('Variable', 2, [('DetectChar(})', 4, 1)]),
                          ('Field', 3, [('Detect2Chars(${)', 6, 2)]),
                          ('Variable', 2, [('DetectChar(})', 9, 1)])])

    def test_return_context_stack(self):
        """Checks if parser returns valid context stack
        """
        syntax = Syntax('debianchangelog.xml')

        self.assertEqual(syntax.parseBlockContextStackTextual('mksv3 (12.06.2-1~ppa1) lucid; urgency=low'),
                         ['INIT', 'Head'])

    def test_use_previous_line_data(self):
        """Pass previous line data to the parser and check, if it uses it
        """
        syntax = Syntax('debianchangelog.xml')
        
        contextStack = [syntax.contexts['INIT'], syntax.contexts['Head']]
        text = ' -- Andrei Kopats <hlamer@tut.by>  Mon, 18 Jun 2012 08:10:32 +0300'
        self.assertEqual(syntax.parseBlockTextualResults(text, contextStack),
                         [])


if __name__ == '__main__':
    unittest.main()
