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
        self.assertEqual(rule.tryMatch(0, '}')[0], 1)
        self.assertEqual(rule.tryMatch(0, 'x')[0], None)

    def test_RegExpr(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 0)
        self.assertEqual(rule.tryMatch(0, '<sadf@example.com> bla bla')[0], len('<sadf@example.com>'))
        self.assertEqual(rule.tryMatch(0, '<sadf@example.com bla bla')[0], None)
        self.assertEqual(rule.tryMatch(0, '<sadf@example.com bla bla')[0], None)
        
        rule = self._getRule('debianchangelog.xml', 'INIT', 0)
        self.assertEqual(rule.tryMatch(0, ' <hlamer@tut.by>')[0], None)  # must not capture 0 symbols
        
        rule = self._getRule('debiancontrol.xml', 'INIT', -2)
        self.assertEqual(rule.tryMatch(0, 'Depends: xxx')[0], len('Depends:'))
        
        rule = self._getRule('fsharp.xml', 'ModuleEnv2', 0)
        self.assertEqual(rule._regExp.pattern, u"[A-Z][A-Za-z\xc0-\xd6\xd8-\xf6\xf8-\xff0-9_']*")
    
    def test_StringDetect(self):
        rule = self._getRule('debiancontrol.xml', 'INIT', 1)
        self.assertEqual(rule.tryMatch(0, 'Recommends: xxx')[0], len('Recommends:'))

    def test_Detect2Chars(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 1)
        self.assertEqual(rule.tryMatch(0, '${xxx}')[0], 2)

    def test_DetectSpaces(self):
        rule = self._getRule('yacc.xml', 'Pre Start', 1)
        self.assertEqual(rule.tryMatch(0, '   asdf fdafasd  ')[0], 3)

    def test_IncludeRules(self):
        rule = self._getRule('yacc.xml', 'Rule In', 0)
        self.assertEqual(rule.tryMatch(0, '/* xxx */')[0], 2)

    def test_AnyChar(self):
        rule = self._getRule('asp.xml', 'aspsource', 12)
        self.assertEqual(rule.tryMatch(0, 'xyz')[0], None)
        self.assertEqual(rule.tryMatch(0, '{}=')[0], 1)

    def test_WordDetect(self):
        rule = self._getRule('qml.xml', 'Normal', 1)
        self.assertEqual(rule.tryMatch(0, 'import')[0], 6)
        self.assertEqual(rule.tryMatch(0, ' import')[0], None)
        
        self.assertEqual(rule.tryMatch(1, ' import')[0], 6)
        self.assertEqual(rule.tryMatch(1, '.import')[0], 6)
        self.assertEqual(rule.tryMatch(1, 'ximport')[0], None)

        self.assertEqual(rule.tryMatch(1, ' import.')[0], 6)
        self.assertEqual(rule.tryMatch(1, '.import ')[0], 6)
        self.assertEqual(rule.tryMatch(1, '-importx')[0], None)

    def test_Int(self):
        rule = self._getRule('apache.xml', 'Integer Directives', 1)
        self.assertEqual(rule.tryMatch(0, '756 items')[0], 3)
        self.assertEqual(rule.tryMatch(0, 'x756 items')[0], None)
        
        rule = self._getRule('c.xml', 'Normal', 13)
        self.assertEqual(rule.tryMatch(0, '756LUL')[0], 6)
        self.assertEqual(rule.tryMatch(0, '756LOL')[0], 4)

    def test_Float(self):
        rule = self._getRule('c.xml', 'Normal', 10)

        self.assertEqual(rule.tryMatch(0, '756')[0], None)
        self.assertEqual(rule.tryMatch(0, '.756')[0], 4)
        self.assertEqual(rule.tryMatch(0, '.75x')[0], 3)
        self.assertEqual(rule.tryMatch(0, '43.75x')[0], 5)
        self.assertEqual(rule.tryMatch(0, '4375..x')[0], 5)
        
        self.assertEqual(rule.tryMatch(0, '4375.f')[0], 6)
        self.assertEqual(rule.tryMatch(0, '4375.v')[0], 5)
        
        self.assertEqual(rule.tryMatch(0, '4E')[0], None)
        self.assertEqual(rule.tryMatch(0, '4E+10')[0], 5)
        self.assertEqual(rule.tryMatch(0, '4E+10F')[0], 6)

    def test_HlCOct(self):
        rule = self._getRule("commonlisp.xml", "SpecialNumber", 2)
        
        self.assertEqual(rule.tryMatch(0, 'xxx')[0], None)
        self.assertEqual(rule.tryMatch(0, '0765')[0], 4)
        self.assertEqual(rule.tryMatch(0, '0865')[0], None)
        self.assertEqual(rule.tryMatch(0, '0768')[0], 3)
        self.assertEqual(rule.tryMatch(0, '076L')[0], 4)

    def test_HlCHex(self):
        rule = self._getRule("cgis.xml", "Common", 9)
        
        self.assertEqual(rule.tryMatch(0, 'xxx')[0], None)
        self.assertEqual(rule.tryMatch(0, '0x76A')[0], 5)
        self.assertEqual(rule.tryMatch(0, '0X0')[0], 3)
        self.assertEqual(rule.tryMatch(0, 'x8')[0], None)
        self.assertEqual(rule.tryMatch(0, '0X76L')[0], 5)
        self.assertEqual(rule.tryMatch(0, '0X76L')[0], 5)
        self.assertEqual(rule.tryMatch(0, '0X76KL')[0], 4)

    def test_HlCStringChar(self):
        rule = self._getRule("boo.xml", "Tripple A-string", 0)
        
        self.assertEqual(rule.tryMatch(0, '\\a')[0], 2)
        self.assertEqual(rule.tryMatch(0, '\\m')[0], None)
        self.assertEqual(rule.tryMatch(0, '\\x56fel')[0], 6)
        self.assertEqual(rule.tryMatch(0, '\\0')[0], 2)
        self.assertEqual(rule.tryMatch(0, '\\078')[0], 3)

    def test_HlCChar(self):
        rule = self._getRule("uscript.xml", "Normal", 6)
        
        self.assertEqual(rule.tryMatch(0, "'A'")[0], 3)
        self.assertEqual(rule.tryMatch(0, "A'")[0], None)
        self.assertEqual(rule.tryMatch(0, "'A")[0], None)
        self.assertEqual(rule.tryMatch(0, "'\\x56fe'")[0], 8)


    def test_RangeDetect(self):
        rule = self._getRule("ini.xml", "ini", 0)
        
        self.assertEqual(rule.tryMatch(0, "[hello]")[0], 7)
        self.assertEqual(rule.tryMatch(0, "[hello] ")[0], 7)
        self.assertEqual(rule.tryMatch(0, "[hello ")[0], None)
        self.assertEqual(rule.tryMatch(0, "][hello ")[0], None)

    def test_LineContinue(self):
        rule = self._getRule("picsrc.xml", "string", 0)
        
        self.assertEqual(rule.tryMatch(0, "\\")[0], 1)
        self.assertEqual(rule.tryMatch(0, "\\ ")[0], None)
        self.assertEqual(rule.tryMatch(0, " \\")[0], None)
        self.assertEqual(rule.tryMatch(0, "x")[0], None)


if __name__ == '__main__':
    unittest.main()
