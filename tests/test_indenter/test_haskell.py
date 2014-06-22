#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

from indenttest import IndentTest


class Test(IndentTest):
    LANGUAGE = 'Haskell'
    INDENT_WIDTH = 4

    @unittest.skip("Haskell not supported yet")
    def test_dontIndent1(self):
        origin = [
            "main = do",
            "    -- This is a comment",
            "    something",
            "    something",
            "",
            ""]
        expected = [
            "main = do",
            "    -- This is a comment",
            "    something",
            "    something",
            "",
            "    foo bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,0);
        self.enter();
        self.type("foo bar");

        self.verifyExpected(expected)

    @unittest.skip("Haskell not supported yet")
    def test_if2(self):
        origin = [
            "foo = if true",
            "         then 1"]
        expected = [
            "foo = if true",
            "         then 1",
            "         else 2"]

        self.setOrigin(origin)

        self.setCursorPosition(1,16);
        self.enter();
        self.type("else 2");

        self.verifyExpected(expected)

    @unittest.skip("Haskell not supported yet")
    def test_afterComma1(self):
        origin = [
            "primitives = [("+", numericBinop (+)),",
            ""]
        expected = [
            "primitives = [("+", numericBinop (+)),",
            "    ("-", numericBinop (-)),",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,39);
        self.enter();
        self.type("(\"-\", numericBinop (-)),");

        self.verifyExpected(expected)

    @unittest.skip("Haskell not supported yet")
    def test_parsec1(self):
        origin = [
            "parseExpr = parseString",
            "        <|> parseNumber",
            ""]
        expected = [
            "parseExpr = parseString",
            "        <|> parseNumber",
            "        <|> parseAtom",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();
        self.type("<|> parseAtom");

        self.verifyExpected(expected)

    @unittest.skip("Haskell not supported yet")
    def test_if1(self):
        origin = [
            "foo = if true",
            ""]
        expected = [
            "foo = if true",
            "         then",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,13);
        self.enter();
        self.type("then");

        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()
