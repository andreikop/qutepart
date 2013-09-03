#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))
from qutepart import Qutepart


class Test(unittest.TestCase):
    """Base class for tests
    """
    app = QApplication(sys.argv)  # app crashes, if created more than once
    
    def setUp(self):
        self.qpart = Qutepart()
    
    def tearDown(self):
        del self.qpart

    def test_overwrite_edit(self):
        self.qpart.show()
        self.qpart.text = 'abcd'
        QTest.keyClicks(self.qpart, "stu")
        self.assertEqual(self.qpart.text, 'stuabcd')
        QTest.keyClick(self.qpart, Qt.Key_Insert)
        QTest.keyClicks(self.qpart, "xy")
        self.assertEqual(self.qpart.text, 'stuxycd')
        QTest.keyClick(self.qpart, Qt.Key_Insert)
        QTest.keyClicks(self.qpart, "z")
        self.assertEqual(self.qpart.text, 'stuxyzcd')

    def test_overwrite_backspace(self):
        self.qpart.show()
        self.qpart.text = 'abcd'
        QTest.keyClick(self.qpart, Qt.Key_Insert)
        for i in range(3):
            QTest.keyClick(self.qpart, Qt.Key_Right)
        for i in range(2):
            QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self.assertEqual(self.qpart.text, 'a  d')


if __name__ == '__main__':
    unittest.main()
