#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt, QPoint
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4.QtTest import QTest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))
from qutepart import Qutepart


class Test(unittest.TestCase):
    """Base class for tests
    """
    app = QApplication(sys.argv)  # app crashes, if created more than once
    
    def setUp(self):
        self._window = QMainWindow()
        self.qpart = Qutepart()
        self._window.setCentralWidget(self.qpart)
        self._window.menuBar().addAction(self.qpart.invokeCompletionAction)
    
    def tearDown(self):
        del self.qpart

    def test_down_selects_first(self):
        self.qpart.text = 'aaaa\nbbbb\ncccX\ndddd\ncccY'
        QTest.keyClicks(self.qpart, "ccc")
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.text, 'cccX\naaaa\nbbbb\ncccX\ndddd\ncccY')
        
    def test_down_selects_second(self):
        self.qpart.text = 'aaaa\nbbbb\ncccX\ndddd\ncccY'
        QTest.keyClicks(self.qpart, "ccc")
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.text, 'cccY\naaaa\nbbbb\ncccX\ndddd\ncccY')
    
    @unittest.skip("Crashes Qt 4.8.3")
    def test_click_selects_first(self):
        self.qpart.text = 'aaaa\nbbbb\ncccX\ndddd\ncccY'
        QTest.keyClicks(self.qpart, "ccc")
        QTest.mouseClick(self.qpart, Qt.LeftButton)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.text, 'cccY\naaaa\nbbbb\ncccX\ndddd\ncccY')
        
    def test_tab_completes(self):
        self.qpart.text = 'aaaaa\naaaaaXXXXX\n'
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "aaa")
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaa')
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaaXXXXX')

    def test_manual(self):
        self._window.show()
        
        self.qpart.text = 'aaaaa\naaaaaXXXXX\n'
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "a")
        
        QTest.keyPress(self.qpart, Qt.Key_Space, Qt.ControlModifier, 100)
        
        QTest.keyClicks(self.qpart, "a")
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaa')


if __name__ == '__main__':
    unittest.main()
