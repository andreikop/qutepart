#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')
from qutepart.syntax_manager import SyntaxManager
from qutepart.Syntax import Context, _ContextStack

def tryMatch(rule, column, text):
    fakeStack = _ContextStack([rule.parentContext, rule.parentContext, rule.parentContext], [None, None, None])
    return rule.tryMatch(fakeStack, column, text)[1]

class Test(unittest.TestCase):
    def _getRule(self, syntaxName, contextName, ruleIndex):
        syntax = SyntaxManager().getSyntaxByXmlName(syntaxName)
        context = syntax.contexts[contextName]
        return context.rules[ruleIndex]
    
    def test_DetectChar(self):
        rule = self._getRule('debiancontrol.xml', 'Variable', 0)
        self.assertEqual(tryMatch(rule, 0, '}'), 1)
        self.assertEqual(tryMatch(rule, 0, 'x'), None)

    def test_RegExpr(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 0)
        self.assertEqual(tryMatch(rule, 0, '<sadf@example.com> bla bla'), len('<sadf@example.com>'))
        self.assertEqual(tryMatch(rule, 0, '<sadf@example.com bla bla'), None)
        self.assertEqual(tryMatch(rule, 0, '<sadf@example.com bla bla'), None)
        
        rule = self._getRule('debianchangelog.xml', 'INIT', 0)
        self.assertEqual(tryMatch(rule, 0, ' <hlamer@tut.by>'), None)  # must not capture 0 symbols
        
        rule = self._getRule('debiancontrol.xml', 'INIT', -2)
        self.assertEqual(tryMatch(rule, 0, 'Depends: xxx'), len('Depends:'))
        
        rule = self._getRule('fsharp.xml', 'ModuleEnv2', 0)
        self.assertEqual(rule._regExp.pattern, u"[A-Z][A-Za-z\xc0-\xd6\xd8-\xf6\xf8-\xff0-9_']*")
    
    def test_StringDetect(self):
        rule = self._getRule('debiancontrol.xml', 'INIT', 1)
        self.assertEqual(tryMatch(rule, 0, 'Recommends: xxx'), len('Recommends:'))

    def test_Detect2Chars(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 1)
        self.assertEqual(tryMatch(rule, 0, '${xxx}'), 2)

    def test_DetectSpaces(self):
        rule = self._getRule('yacc.xml', 'Pre Start', 1)
        self.assertEqual(tryMatch(rule, 0, '   asdf fdafasd  '), 3)

    def test_IncludeRules(self):
        rule = self._getRule('yacc.xml', 'Rule In', 0)
        self.assertEqual(tryMatch(rule, 0, '/* xxx */'), 2)

    def test_IncludeRulesExternal(self):
        rule = self._getRule('javascript.xml', 'Comment', 1)  # external context ##Alerts
        self.assertEqual(tryMatch(rule, 1, ' NOTE hello, world'), 4)
        self.assertEqual(tryMatch(rule, 1, ' NOET hello, world'), None)

    def test_AnyChar(self):
        rule = self._getRule('asp.xml', 'aspsource', 12)
        self.assertEqual(tryMatch(rule, 0, 'xyz'), None)
        self.assertEqual(tryMatch(rule, 0, '{}='), 1)

    def test_WordDetect(self):
        rule = self._getRule('qml.xml', 'Normal', 1)
        self.assertEqual(tryMatch(rule, 0, 'import'), 6)
        self.assertEqual(tryMatch(rule, 0, ' import'), None)
        
        self.assertEqual(tryMatch(rule, 1, ' import'), 6)
        self.assertEqual(tryMatch(rule, 1, '.import'), 6)
        self.assertEqual(tryMatch(rule, 1, 'ximport'), None)

        self.assertEqual(tryMatch(rule, 1, ' import.'), 6)
        self.assertEqual(tryMatch(rule, 1, '.import '), 6)
        
        self.assertEqual(tryMatch(rule, 1, '-importx'), None)
        self.assertEqual(tryMatch(rule, 1, 'importx'), None)

    def test_Int(self):
        rule = self._getRule('apache.xml', 'Integer Directives', 1)
        self.assertEqual(tryMatch(rule, 0, '756 items'), 3)
        self.assertEqual(tryMatch(rule, 0, 'x756 items'), None)
        
        rule = self._getRule('c.xml', 'Normal', 13)
        self.assertEqual(tryMatch(rule, 0, '756LUL'), 6)
        self.assertEqual(tryMatch(rule, 0, '756LOL'), 4)

    def test_Float(self):
        rule = self._getRule('c.xml', 'Normal', 10)

        self.assertEqual(tryMatch(rule, 0, '756'), None)
        self.assertEqual(tryMatch(rule, 0, '.756'), 4)
        self.assertEqual(tryMatch(rule, 0, '.75x'), 3)
        self.assertEqual(tryMatch(rule, 0, '43.75x'), 5)
        self.assertEqual(tryMatch(rule, 0, '4375..x'), 5)
        
        self.assertEqual(tryMatch(rule, 0, '4375.f'), 6)
        self.assertEqual(tryMatch(rule, 0, '4375.v'), 5)
        
        self.assertEqual(tryMatch(rule, 0, '4E'), None)
        self.assertEqual(tryMatch(rule, 0, '4E+10'), 5)
        self.assertEqual(tryMatch(rule, 0, '4E+10F'), 6)

    def test_HlCOct(self):
        rule = self._getRule("commonlisp.xml", "SpecialNumber", 2)
        
        self.assertEqual(tryMatch(rule, 0, 'xxx'), None)
        self.assertEqual(tryMatch(rule, 0, '0765'), 4)
        self.assertEqual(tryMatch(rule, 0, '0865'), None)
        self.assertEqual(tryMatch(rule, 0, '0768'), 3)
        self.assertEqual(tryMatch(rule, 0, '076L'), 4)

    def test_HlCHex(self):
        rule = self._getRule("cgis.xml", "Common", 9)
        
        self.assertEqual(tryMatch(rule, 0, 'xxx'), None)
        self.assertEqual(tryMatch(rule, 0, '0x76A'), 5)
        self.assertEqual(tryMatch(rule, 0, '0X0'), 3)
        self.assertEqual(tryMatch(rule, 0, 'x8'), None)
        self.assertEqual(tryMatch(rule, 0, '0X76L'), 5)
        self.assertEqual(tryMatch(rule, 0, '0X76L'), 5)
        self.assertEqual(tryMatch(rule, 0, '0X76KL'), 4)

    def test_HlCStringChar(self):
        rule = self._getRule("boo.xml", "Tripple A-string", 0)
        
        self.assertEqual(tryMatch(rule, 0, '\\a'), 2)
        self.assertEqual(tryMatch(rule, 0, '\\m'), None)
        self.assertEqual(tryMatch(rule, 0, '\\x56fel'), 6)
        self.assertEqual(tryMatch(rule, 0, '\\0'), 2)
        self.assertEqual(tryMatch(rule, 0, '\\078'), 3)

    def test_HlCChar(self):
        rule = self._getRule("uscript.xml", "Normal", 6)
        
        self.assertEqual(tryMatch(rule, 0, "'A'"), 3)
        self.assertEqual(tryMatch(rule, 0, "A'"), None)
        self.assertEqual(tryMatch(rule, 0, "'A"), None)
        self.assertEqual(tryMatch(rule, 0, "'\\x56fe'"), 8)


    def test_RangeDetect(self):
        rule = self._getRule("ini.xml", "ini", 0)
        
        self.assertEqual(tryMatch(rule, 0, "[hello]"), 7)
        self.assertEqual(tryMatch(rule, 0, "[hello] "), 7)
        self.assertEqual(tryMatch(rule, 0, "[hello "), None)
        self.assertEqual(tryMatch(rule, 0, "][hello "), None)

    def test_LineContinue(self):
        rule = self._getRule("picsrc.xml", "string", 0)
        
        self.assertEqual(tryMatch(rule, 0, "\\"), 1)
        self.assertEqual(tryMatch(rule, 0, "\\ "), None)
        self.assertEqual(tryMatch(rule, 0, " \\"), None)
        self.assertEqual(tryMatch(rule, 0, "x"), None)

    def test_DetectIdentifier(self):
        rule = self._getRule("dtd.xml", "Normal", 7)
        
        self.assertEqual(tryMatch(rule, 0, " asdf"), None)
        self.assertEqual(tryMatch(rule, 0, "asdf"), 4)
        self.assertEqual(tryMatch(rule, 0, "asdf+"), 4)
        self.assertEqual(tryMatch(rule, 0, "asdf7"), 5)
        self.assertEqual(tryMatch(rule, 0, "7asdf7"), None)

    def test_keyword(self):
        rule = self._getRule("javascript.xml", "Normal", 6)
        
        self.assertEqual(tryMatch(rule, 0, "var"), 3)
        self.assertEqual(tryMatch(rule, 0, "vor"), None)
        
        self.assertEqual(tryMatch(rule, 1, " var "), 3)
        self.assertEqual(tryMatch(rule, 1, " varx "), None)
        self.assertEqual(tryMatch(rule, 2, " xvar "), None)
    
    def test_lookahead(self):
        rule = self._getRule("javascript.xml", "ObjectMember", 3)
        text = 'g.r( /dooh/ )'
        self.assertEqual(tryMatch(rule, 3, text), 0)

    def test_firstNonSpace(self):
        rule = self._getRule("makefile.xml", "Normal", 2)
        
        #self.assertEqual(tryMatch(rule, 0, "all: pre"), 4)
        self.assertEqual(tryMatch(rule, 1, " all: pre"), None)

    def test_dynamic_reg_exp(self):
        """RegExpr rule, dynamic=true
        """
        rule = self._getRule("ruby.xml", "gdl_dq_string_5", 2)  # "\s*%1"
        text = '%|a| x'
        fakeStack = _ContextStack([rule.parentContext, rule.parentContext, rule.parentContext],
                                  [('|'), ('|'), ('|')]
                                 )
        newStack, count, matchedRule = rule.tryMatch(fakeStack, 3, text)
        self.assertEqual(count, 1)

    def test_dynamic_string_detect(self):
        """StringDetect rule, dynamic=true
        """
        rule = self._getRule("php.xml", "phpsource", 29)  # heredoc
        text = "<<<myheredoc"

        fakeStack = _ContextStack([rule.parentContext, rule.parentContext, rule.parentContext],
                                  [None, None, ('myheredoc',)]
                                 )
        newStack, count, matchedRule = rule.tryMatch(fakeStack, 0, text)
        self.assertEqual(count, len(text))

    def test_dynamic_string_detect(self):
        """DetectChar rule, dynamic=true
        """
        rule = self._getRule("perl.xml", "string_6", 3)
        text = "abcdXefg"

        fakeStack = _ContextStack([rule.parentContext, rule.parentContext, rule.parentContext],
                                  [None, None, ('X', 'Y', 'Z',)]
                                 )
        newStack, count, matchedRule = rule.tryMatch(fakeStack, 0, text)
        self.assertEqual(count, None)

        newStack, count, matchedRule = rule.tryMatch(fakeStack, 4, text)
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
