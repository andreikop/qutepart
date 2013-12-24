#!/usr/bin/env python

import unittest

from indenttest import IndentTest


class Test(IndentTest):
    LANGUAGE = 'Python'
    INDENT_WIDTH = 2
    
    def test_dedentReturn(self):
        origin = [
            "def some_function():",
            "  return"]
        expected = [
            "def some_function():",
            "  return",
            "pass"]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_dedentContinue(self):
        origin = [
            "while True:",
            "  continue"]
        expected = [
            "while True:",
            "  continue",
            "pass"]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_keepIndent2(self):
        origin = [
            "class my_class():",
            "  def my_fun():",
            '    print "Foo"',
            "    print 3"]
        expected = [
            "class my_class():",
            "  def my_fun():",
            '    print "Foo"',
            "    print 3",
            "    pass"]

        self.setOrigin(origin)

        self.setCursorPosition(3, 12);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_keepIndent4(self):
        origin = [
            "def some_function():"]
        expected = [
            "def some_function():",
            "  pass",
            "",
            "pass"]

        self.setOrigin(origin)

        self.setCursorPosition(0,22);
        self.enter();
        self.type("pass");
        self.enter()
        self.enter()
        self.type("pass");
        self.verifyExpected(expected)

    def test_dedentRaise(self):
        origin = [
            "try:",
            "  raise"]
        expected = [
            "try:",
            "  raise",
            "except:"]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("except:");
        self.verifyExpected(expected)

    def test_indentColon(self):
        origin = [
            "def some_function(param, param2):"]
        expected = [
            "def some_function(param, param2):",
            "  pass"]

        self.setOrigin(origin)

        self.setCursorPosition(0,34);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_dedentPass(self):
        origin = [
            "def some_function():",
            "  pass"]
        expected = [
            "def some_function():",
            "  pass",
            "pass"]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_dedentBreak(self):
        origin = [
            "def some_function():",
            "  return"]
        expected = [
            "def some_function():",
            "  return",
            "pass"]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_keepIndent3(self):
        origin = [
            "while True:",
            "  returnFunc()",
            "  myVar = 3"]
        expected = [
            "while True:",
            "  returnFunc()",
            "  myVar = 3",
            "  pass"]

        self.setOrigin(origin)

        self.setCursorPosition(2, 12);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_keepIndent1(self):
        origin = [
            "def some_function(param, param2):",
            "  a = 5",
            "  b = 7"]
        expected = [
            "def some_function(param, param2):",
            "  a = 5",
            "  b = 7",
            "  pass"]

        self.setOrigin(origin)

        self.setCursorPosition(2, 8);
        self.enter();
        self.type("pass");
        self.verifyExpected(expected)

    def test_autoIndentAfterEmpty(self):
        origin = [
            "while True:",
            "   returnFunc()",
            "",
            "   myVar = 3"]
        expected = [
            "while True:",
            "   returnFunc()",
            "",
            "   x",
            "   myVar = 3"]

        self.setOrigin(origin)

        self.setCursorPosition(2, 0);
        self.enter();
        self.tab();
        self.type("x");
        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()
