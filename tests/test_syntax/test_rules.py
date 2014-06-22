#!/usr/bin/env python3

import unittest

import sys
import os.path

topLevelPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, topLevelPath)
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.6/'))
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.7/'))

import qutepart

from qutepart.syntax import SyntaxManager

import qutepart.syntax.loader

parser = qutepart.syntax.loader._parserModule

_currentSyntax = None

def tryMatch(rule, column, text):
    return tryMatchWithData(rule, None, column, text)

def tryMatchWithData(rule, contextData, column, text):
    textToMatchObject = parser.TextToMatchObject(column, str(text), _currentSyntax.parser.deliminatorSet, contextData)
    ruleTryMatchResult = rule.tryMatch(textToMatchObject)
    if ruleTryMatchResult is not None:
        return ruleTryMatchResult.length
    else:
        return None


class Test(unittest.TestCase):
    def _getRule(self, syntaxName, contextName, ruleIndex):
        global _currentSyntax
        _currentSyntax = SyntaxManager().getSyntax(xmlFileName=syntaxName)
        context = _currentSyntax.parser.contexts[contextName]
        return context.rules[ruleIndex]

    def test_DetectChar(self):
        rule = self._getRule('debiancontrol.xml', 'Variable', 0)
        self.assertEqual(tryMatch(rule, 0, '}'), 1)
        self.assertEqual(tryMatch(rule, 0, 'x'), None)

    def test_DetectChar_dynamic(self):
        """DetectChar rule, dynamic=true
        """
        rule = self._getRule("perl.xml", "ip_string_6", 1)
        text = "a"

        self.assertEqual(tryMatchWithData(rule, ('a', 'b', 'c'), 0, text), 1)
        self.assertEqual(tryMatchWithData(rule, ('x', 'y', 'z'), 0, text), None)

    def test_DetectChar_dynamic2(self):
        rule = self._getRule("perl.xml", "string_6", 3)
        text = "abcdXefg"

        count = tryMatchWithData(rule, ('X', 'Y', 'Z',), 0, text)
        self.assertEqual(count, None)

        count = tryMatchWithData(rule, ('X', 'Y', 'Z',), 4, text)
        self.assertEqual(count, 1)

    def test_Detect2Chars(self):
        rule = self._getRule('debiancontrol.xml', 'Field', 1)
        self.assertEqual(tryMatch(rule, 0, '${xxx}'), 2)

    def test_Detect2Chars_shell_escape(self):
        """Test escape characters processing in Detect2Chars rule
        """
        rule = self._getRule('zsh.xml', "FindStrings", 1)
        self.assertEqual(tryMatch(rule, 0, '\\"'), 2)

    def test_AnyChar(self):
        rule = self._getRule('asp.xml', 'aspsource', 12)
        self.assertEqual(tryMatch(rule, 0, 'xyz'), None)
        self.assertEqual(tryMatch(rule, 0, '{}='), 1)

    def test_StringDetect(self):
        rule = self._getRule('debiancontrol.xml', 'INIT', 1)
        self.assertEqual(tryMatch(rule, 0, 'Recommends: xxx'), len('Recommends:'))

    def test_StringDetect_first_non_space(self):
        """StringDetect with firstNonSpace=true
        """
        rule = self._getRule('d.xml', 'normal', 9)
        self.assertEqual(tryMatch(rule, 2, '  //BEGIN'), len('//BEGIN'))

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

    def test_keyword(self):
        rule = self._getRule("javascript.xml", "Normal", 8)

        self.assertEqual(tryMatch(rule, 0, "var"), 3)
        self.assertEqual(tryMatch(rule, 0, "vor"), None)

        self.assertEqual(tryMatch(rule, 1, " var "), 3)
        self.assertEqual(tryMatch(rule, 1, " varx "), None)
        self.assertEqual(tryMatch(rule, 2, " xvar "), None)

    def test_jsp_keyword(self):
        rule = self._getRule('jsp.xml', "Jsp Scriptlet", 5)
        self.assertEqual(tryMatch(rule, 0, "String"), len("String"))

    def test_mup_keyword(self):
        """Test for additionalDeliminator syntax attribute
        """
        rule = self._getRule('mup.xml', "Value", 2)
        text = 'key = 3#minor'
        self.assertEqual(tryMatch(rule, 8, text), 5)

    def test_keyword_insensitive(self):
        """Insensitive attribute for particular keyword
        """
        rule = self._getRule("cmake.xml", "Normal Text", 11)
        self.assertEqual(tryMatch(rule, 0, "ADD_definitions()"), len("ADD_definitions"))

    def test_keyword_insensitive_syntax(self):
        """Insensitive attribute for whole syntax
        """
        rule = self._getRule("css.xml", "RuleSet", 1)
        self.assertEqual(tryMatch(rule, 0, "backGround"), len("backGround"))

    def test_keyword_weak_delimiter(self):
        """Test weakDeliminator attribute parsing and usage
        """
        rule = self._getRule("css.xml", "RuleSet", 1)
        self.assertEqual(tryMatch(rule, 0, "background-color"), len("background-color"))

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
        if hasattr(rule, 'regExp'):  # only on Python version
            self.assertEqual(rule.regExp.pattern, "[A-Z][A-Za-z\xc0-\xd6\xd8-\xf6\xf8-\xff0-9_']*")

    def test_RegExpr_slashB(self):
        rule = self._getRule('fortran.xml', 'find_numbers', 3)
        self.assertEqual(tryMatch(rule, 5, 'point3d'), None)
        self.assertEqual(tryMatch(rule, 5, 'poin(3)'), 1)
        self.assertEqual(tryMatch(rule, 5, 'poin 3 '), 1)

    def test_RegExpr_caret(self):
        rule = self._getRule('fortran.xml', 'find_decls', 7)
        self.assertEqual(tryMatch(rule, 1, ' real'), None)
        self.assertEqual(tryMatch(rule, 0, 'real'), 4)

    def test_Int(self):
        rule = self._getRule('apache.xml', 'Integer Directives', 1)
        self.assertEqual(tryMatch(rule, 0, '756 items'), 3)
        self.assertEqual(tryMatch(rule, 0, 'x756 items'), None)

        rule = self._getRule('c.xml', 'Normal', 14)
        self.assertEqual(tryMatch(rule, 0, '756LUL'), 6)
        self.assertEqual(tryMatch(rule, 0, '756LUL'), 6)
        self.assertEqual(tryMatch(rule, 0, '756LOL'), 4)

        self.assertEqual(tryMatch(rule, 1, '(756LOL'), 4)
        self.assertEqual(tryMatch(rule, 1, 'i756LOL'), None)

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

        self.assertEqual(tryMatch(rule, 0, '4e+10'), 5)  # lower case

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

    def test_IncludeRules(self):
        rule = self._getRule('yacc.xml', 'Rule In', 0)
        self.assertEqual(tryMatch(rule, 0, '/* xxx */'), 2)

    def test_IncludeRulesExternal(self):
        rule = self._getRule('javascript.xml', 'Comment', 0)  # external context ##Alerts
        self.assertEqual(tryMatch(rule, 1, ' NOTE hello, world'), 4)
        self.assertEqual(tryMatch(rule, 1, ' NOET hello, world'), None)

    def test_DetectSpaces(self):
        rule = self._getRule('yacc.xml', 'Pre Start', 1)
        self.assertEqual(tryMatch(rule, 0, '   asdf fdafasd  '), 3)

    def test_DetectIdentifier(self):
        rule = self._getRule("dtd.xml", "Normal", 7)

        self.assertEqual(tryMatch(rule, 0, " asdf"), None)
        self.assertEqual(tryMatch(rule, 0, "asdf"), 4)
        self.assertEqual(tryMatch(rule, 0, "asdf+"), 4)
        self.assertEqual(tryMatch(rule, 0, "asdf7"), 5)
        self.assertEqual(tryMatch(rule, 0, "7asdf7"), None)

    def test_lookahead(self):
        rule = self._getRule("javascript.xml", "NoRegExp", 0)
        text = '//'
        self.assertEqual(tryMatch(rule, 0, text), 0)

    def test_firstNonSpace(self):
        rule = self._getRule("d.xml", "DdocBlock", 3)

        self.assertEqual(tryMatch(rule, 1, "x*"), None)
        self.assertEqual(tryMatch(rule, 1, " *"), 1)

    def test_dynamic_reg_exp(self):
        """RegExpr rule, dynamic=true
        """
        rule = self._getRule("ruby.xml", "gdl_dq_string_5", 2)  # "\s*%1"
        text = '%|a| x'
        count = tryMatchWithData(rule, ('blabla|', '|', ), 3, text)
        self.assertEqual(count, 1)

    def test_dynamic_string_detect(self):
        """StringDetect rule, dynamic=true
        """
        rule = self._getRule("php.xml", "phpsource", 34)  # heredoc
        text = "<<<myheredoc"

        count = tryMatchWithData(rule, ('myheredoc',), 0, text)
        self.assertEqual(count, len(text))


if __name__ == '__main__':
    unittest.main()
