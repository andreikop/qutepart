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
        syntax = Syntax('debiancontrol.xml')

        self.assertEqual(syntax.parseBlockContextStackTextual('Source: mksv3'),
                         ['INIT'])

    def test_line_end_context_switch(self):
        """Switch context, if line end reached, and current context has lineEndContext attribute
        """
        syntax = Syntax('debianchangelog.xml')
        
        text = 'mksv3 '
        self.assertEqual(syntax.parseBlockContextStackTextual(text),
                         ['INIT'])

    '''
    def test_fallgrhough(self):
        """Switch context, if no rules matched
        """
        syntax = Syntax('yacc.xml')
        
        text = 'mksv3 '
        self.assertEqual(syntax.parseBlockContextStackTextual(text),
                         ['INIT'])
    '''


if __name__ == '__main__':
    unittest.main()
