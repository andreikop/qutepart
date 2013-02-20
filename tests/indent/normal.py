#!/usr/bin/env python

import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

import sys
sys.path.insert(0, '../..')
from qutepart import Qutepart
import qutepart
print qutepart.__file__

class IndentTest(unittest.TestCase):
    app = QApplication(sys.argv)
    
    def setOrigin(self, text):
        self.qpart.text = '\n'.join(text)
    
    def verifyExpected(self, text):
        self.assertEquals(self.qpart.text.split('\n'), text)
    
    def setCursorPosition(self, line, col):
        self.qpart.cursorPosition = line, col
    
    def enter(self):
        QTest.keyClick(self.qpart, Qt.Key_Enter)
    
    def type(self, text):
        QTest.keyClicks(self.qpart, text)

    def setUp(self):
        self.qpart = Qutepart()
        if self.LANGUAGE is not None:
            self.qpart.detectSyntax(language = self.LANGUAGE)

class Test(IndentTest):
    LANGUAGE = None
    
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

    """ now not removing trailing whitespaces
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
    """
    
    def test_emptyline1(self):
        origin = [
            "    totally empty line",
            "",
            ""]
        expected = [
            "    totally empty line",
            "",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,0);
        self.enter();
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

if __name__ == '__main__':
    unittest.main()
