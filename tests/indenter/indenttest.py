import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

import sys
import os
topLevelPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, topLevelPath)
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.6/'))
sys.path.insert(0, os.path.join(topLevelPath, 'build/lib.linux-x86_64-2.7/'))

from qutepart import Qutepart
import qutepart


class IndentTest(unittest.TestCase):
    app = QApplication(sys.argv)

    def setOrigin(self, text):
        self.qpart.text = '\n'.join(text)

    def verifyExpected(self, text):
        lines = self.qpart.text.split('\n')
        self.assertEquals(map(str, lines), text)

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
        self.qpart._autoIndentBlock(self.qpart.document().findBlockByNumber(index), '')

    def alignAll(self):
        QTest.keyClick(self.qpart, Qt.Key_A, Qt.ControlModifier)
        self.qpart.autoIndentLineAction.trigger()

    def setUp(self):
        self.qpart = Qutepart()
        if self.LANGUAGE is not None:
            self.qpart.detectSyntax(language = self.LANGUAGE)
            self.qpart.indentWidth = self.INDENT_WIDTH
