#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest


class Test(IndentTest):
    LANGUAGE = 'Common Lisp'
    INDENT_WIDTH = 2

    def test_three_semicolons(self):
        origin = [
            "      ",
            "   asdf"
            ]
        expected = [
            ";;;",
            "   asdf"
            ]

        self.setOrigin(origin)

        self.setCursorPosition(0, 6);
        self.type(";;;");
        self.verifyExpected(expected)

    def test_two_semicolons(self):
        origin = [
            "      ",
            "   asdf"
            ]
        expected = [
            "   ;;",
            "   asdf"
            ]

        self.setOrigin(origin)

        self.setCursorPosition(0, 6);
        self.type(";;");
        self.verifyExpected(expected)

    def test_find_brace(self):
        origin = [
            "  (bla                   (x (y (z)))",
            ]
        expected = [
            "  (bla                   (x (y (z)))",
            "    "
            ]

        self.setOrigin(origin)

        self.setCursorPosition(0, 36);
        self.enter()
        self.verifyExpected(expected)

    def test_not_found_brace(self):
        origin = [
            "  (bla                   (x (y (z))))",
            ]
        expected = [
            "  (bla                   (x (y (z))))",
            ""
            ]

        self.setOrigin(origin)

        self.setCursorPosition(0, 37);
        self.enter()
        self.verifyExpected(expected)



if __name__ == '__main__':
    unittest.main()
