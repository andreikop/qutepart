#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.Syntax import Syntax

class RulesTestCase(unittest.TestCase):
    def _getRule(self, syntaxName, contextName, ruleIndex):
        syntax = Syntax(syntaxName)
        context = syntax.contexts[contextName]
        return context.rules[ruleIndex]
    
    def test_DetectChar(self):
        rule = self._getRule('debiancontrol.xml', 'Variable', 0)
        self.assertEqual(rule.tryMatch('}'), 1)
        self.assertEqual(rule.tryMatch('x'), None)

    def test_RegExpr(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 0)
        self.assertEqual(rule.tryMatch('<sadf@example.com> bla bla'), len('<sadf@example.com>'))
        self.assertEqual(rule.tryMatch('<sadf@example.com bla bla'), None)
        self.assertEqual(rule.tryMatch('<sadf@example.com bla bla'), None)
        
        rule = self._getRule('debianchangelog.xml', 'INIT', 0)
        self.assertEqual(rule.tryMatch(' <hlamer@tut.by>'), None)  # must not capture 0 symbols
        
        rule = self._getRule('debiancontrol.xml', 'INIT', -2)
        self.assertEqual(rule.tryMatch('Depends: xxx'), len('Depends:'))
        
        rule = self._getRule('fsharp.xml', 'ModuleEnv2', 0)
        self.assertEqual(rule.String, u"[A-Z][A-Za-z\xc0-\xd6\xd8-\xf6\xf8-\xff0-9_']*")
    
    def test_StringDetect(self):
        rule = self._getRule('debiancontrol.xml', 'INIT', 1)
        self.assertEqual(rule.tryMatch('Recommends: xxx'), len('Recommends:'))

    def test_Detect2Chars(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 1)
        self.assertEqual(rule.tryMatch('${xxx}'), 2)

if __name__ == '__main__':
    unittest.main()
