#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.syntax_manager import SyntaxManager

class RulesTestCase(unittest.TestCase):
    
    def test_basic(self):
        """Just apply rules
        """
        syntax = SyntaxManager().getSyntaxByXmlName('debiancontrol.xml')
        self.assertEqual(syntax.parser.parseBlockTextualResults('Section:'),
                         [('INIT', 8, [(u'RegExpr( [^ ]*: )', 0, 8)])])
        self.assertEqual(syntax.parser.parseBlockTextualResults(' '),
                         [('INIT', 1, [('DetectChar( , 0)', 0, 1)])])
        self.assertEqual(syntax.parser.parseBlockTextualResults('Provides:'),
                         [('INIT', 9, [('StringDetect(Provides:)', 0, 9)])])
    
    def test_rule_switches_context(self):
        """Matched rule switches context
        """
        syntax = SyntaxManager().getSyntaxByXmlName('debiancontrol.xml')
        self.assertEqual(syntax.parser.parseBlockTextualResults('Section: editors'),
                         [('INIT', 8, [(u'RegExpr( [^ ]*: )', 0, 8)]), ('Field', 8, [])])
        self.assertEqual(syntax.parser.parseBlockTextualResults(' Section: editors'),
                         [('INIT', 1, [('DetectChar( , 0)', 0, 1)]), ('Field', 16, [])])
        self.assertEqual(syntax.parser.parseBlockTextualResults('Provides: xxx'),
                         [('INIT', 9, [('StringDetect(Provides:)', 0, 9)]), ('DependencyField', 4, [])])

    def test_pop_context(self):
        """Checks if #pop operation works correctly
        """
        syntax = SyntaxManager().getSyntaxByXmlName('debiancontrol.xml')

        self.assertEqual(syntax.parser.parseBlockTextualResults(' ${a} ${b}'),
                         [('INIT', 1, [('DetectChar( , 0)', 0, 1)]), 
                          ('Field', 2, [('Detect2Chars(${)', 1, 2)]),
                          ('Variable', 2, [('DetectChar(}, 0)', 4, 1)]),
                          ('Field', 3, [('Detect2Chars(${)', 6, 2)]),
                          ('Variable', 2, [('DetectChar(}, 0)', 9, 1)])])

    def test_return_context_stack(self):
        """Checks if parser returns valid context stack
        """
        syntax = SyntaxManager().getSyntaxByXmlName('debiancontrol.xml')

        self.assertEqual(syntax.parser.parseBlockContextStackTextual('Source: mksv3'),
                         ['INIT'])

    def test_line_end_context_switch(self):
        """Switch context, if line end reached, and current context has lineEndContext attribute
        """
        syntax = SyntaxManager().getSyntaxByXmlName('debianchangelog.xml')
        
        text = 'mksv3 '
        self.assertEqual(syntax.parser.parseBlockContextStackTextual(text),
                         ['INIT'])

    def test_just_one_more_test_1(self):
        """Test for one of bugs.
        """
        syntax = SyntaxManager().getSyntaxByXmlName('javascript.xml')
        
        text = " /* */"
        self.assertEqual(syntax.parser.parseBlockTextualResults(text),
                         [('Normal', 3, [('DetectSpaces()', 0, 1),
                                         ('Detect2Chars(/*)', 1, 2)]),
                          ('Multi/inline Comment', 3, [('Detect2Chars(*/)', 4, 2)])])


    '''
    def test_fallgrhough(self):
        """Switch context, if no rules matched
        """
        syntax = SyntaxManager().getSyntaxByXmlName('yacc.xml')
        
        text = 'mksv3 '
        self.assertEqual(syntax.parser.parseBlockContextStackTextual(text),
                         ['INIT'])
    '''


if __name__ == '__main__':
    unittest.main()
