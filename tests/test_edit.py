#!/usr/bin/env python

import sys
import unittest

import base

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

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

    @base.in_main_loop
    def test_overwrite_undo(self):
        self.qpart.show()
        self.qpart.text = 'abcd'
        QTest.keyClick(self.qpart, Qt.Key_Insert)
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_X)
        QTest.keyClick(self.qpart, Qt.Key_X)
        self.assertEqual(self.qpart.text, 'axxd')
        # Ctrl+Z doesn't work. Wtf???
        self.qpart.document().undo()
        self.qpart.document().undo()
        self.assertEqual(self.qpart.text, 'abcd')


if __name__ == '__main__':
    unittest.main()
