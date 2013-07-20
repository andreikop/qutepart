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

    def test_1(self):
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

    def test_rectangular_selection(self):
        self.qpart.show()
        for key in [Qt.Key_Delete, Qt.Key_Backspace]:
            self.qpart.text = 'abcd\nef\nghkl\nmnop'
            QTest.keyClick(self.qpart, Qt.Key_Right)
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, key)
            self.assertEqual(self.qpart.text, 'ad\ne\ngl\nmnop')

    def test_rectangular_selection_reset_by_move(self):
        self.qpart.show()
        self.qpart.text = 'abcd\nef\nghkl\nmnop'
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Left)
        QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self.assertEqual(self.qpart.text, 'abcd\nef\ngkl\nmnop')

    def test_rectangular_selection_reset_by_edit(self):
        self.qpart.show()
        self.qpart.text = 'abcd\nef\nghkl\nmnop'
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClicks(self.qpart, 'x')
        QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self.assertEqual(self.qpart.text, 'abcd\nef\nghkl\nmnop')
    
    def test_rectangular_selection_with_tabs(self):
        self.qpart.show()
        self.qpart.text = 'abcdefghhhhh\n\tklm\n\t\txyz'
        self.qpart.cursorPosition = (0, 6)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Delete)
        self.assertEqual(self.qpart.text, 'abcdefhh\n\tkl\n\t\tz')

if __name__ == '__main__':
    unittest.main()
