#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest


class Test(IndentTest):
    LANGUAGE = None
    INDENT_WIDTH = 4

    def test_normal2(self):
        origin = [
            "    bla bla",
            ""]
        expected = [
            "    bla bla",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    @unittest.skip('Now empty lines are not removed')
    def test_emptyline3(self):
        origin = [
            "    totally empty line",
            "",
            ""]
        expected = [
            "    totally empty line",
            "",
            "",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,0);
        self.enter();
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_emptyline1(self):
        origin = [
            "      totally empty line",
            "",
            ""]
        expected = [
            "      totally empty line",
            "",
            "      ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,0);
        self.enter();
        self.tab();
        self.type("ok");
        self.verifyExpected(expected)

    def test_normal3(self):
        origin = [
            "    bla bla",
            "    blu blu",
            ""]
        expected = [
            "    bla bla",
            "    blu blu",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_cascade1(self):
        origin = [
            "bla bla",
            "    blu blu",
            ""]
        expected = [
            "bla bla",
            "    blu blu",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_emptyline2(self):
        origin = [
            "    empty line padded with 4 spcs",
            "    ",
            ""]
        expected = [
            "    empty line padded with 4 spcs",
            "    ",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,4);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_midbreak1(self):
        origin = [
            "    bla bla    blu blu",
            ""]
        expected = [
            "    bla bla",
            "    blu blu",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();

        self.verifyExpected(expected)

    def test_midbreak2(self):
        origin = [
            "    bla bla blu blu",
            ""]
        expected = [
            "    bla bla",
            "    blu blu",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();

        self.verifyExpected(expected)

    def test_normal1(self):
        origin = [
            "bla bla",
            ""]
        expected = [
            "bla bla",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,7);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_newline(self):
        origin = [
            "    sadf",
            "",
            ""]
        expected = [
            "    sadf",
            "",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,0);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)



class Test(IndentTest):
    """Lua uses normal indenter. Check it doesn't crash at least
    """
    LANGUAGE = 'Lua'
    INDENT_WIDTH = 4

    def test_normal2(self):
        origin = [
            "    bla bla",
            ""]
        expected = [
            "    bla bla",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()
