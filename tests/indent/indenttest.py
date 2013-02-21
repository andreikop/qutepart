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

    def alignLine(self, index):
        raise NotImplemented()
    
    def setUp(self):
        self.qpart = Qutepart()
        if self.LANGUAGE is not None:
            self.qpart.detectSyntax(language = self.LANGUAGE)
            self.qpart.indentWidth = self.INDENT_WIDTH
