import unittest

import sip
sip.setapi('QString', 2)

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import sys
import os
topLevelPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, topLevelPath)
sys.path.insert(0, os.path.join(topLevelPath, 'tests'))

from qutepart import Qutepart
import qutepart
import base


class IndentTest(unittest.TestCase):
    app = base.papp

    def setOrigin(self, text):
        self.qpart.text = '\n'.join(text)

    def verifyExpected(self, text):
        lines = self.qpart.text.split('\n')
        self.assertEqual(text, [l for l in lines])

    def setCursorPosition(self, line, col):
        self.qpart.cursorPosition = line, col

    def enter(self):
        QTest.keyClick(self.qpart, Qt.Key_Enter)

    def tab(self):
        QTest.keyClick(self.qpart, Qt.Key_Tab)

    def type(self, text):
        QTest.keyClicks(self.qpart, text)

    def writeCursorPosition(self):
        line, col = self.qpart.cursorPosition
        text = '(%d,%d)' % (line, col)
        self.type(text)

    def writeln(self):
        self.qpart.textCursor().insertText('\n')

    def alignLine(self, index):
        self.qpart._indenter.autoIndentBlock(self.qpart.document().findBlockByNumber(index), '')

    def alignAll(self):
        QTest.keyClick(self.qpart, Qt.Key_A, Qt.ControlModifier)
        self.qpart.autoIndentLineAction.trigger()

    def setUp(self):
        self.qpart = Qutepart()
        if self.LANGUAGE is not None:
            self.qpart.detectSyntax(language = self.LANGUAGE)
            self.qpart.indentWidth = self.INDENT_WIDTH
