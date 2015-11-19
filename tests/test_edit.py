#!/usr/bin/env python

import sys
import unittest

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from qutepart import Qutepart


class Test(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

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

    def test_alt_does_not_type(self):
        """ By default when Alt+Key is pressed - text is inserted.
        Qutepart ignores this key pressings
        """
        QTest.keyClick(self.qpart, Qt.Key_A, Qt.AltModifier)
        self.assertEqual(self.qpart.text, '')
        QTest.keyClick(self.qpart, Qt.Key_A)
        self.assertEqual(self.qpart.text, 'a')

    def test_home1(self):
        """ Test the operation of the home key. """

        self.qpart.show()
        self.qpart.text = '  xx'
        # Move to the end of this string.
        self.qpart.cursorPosition = (100, 100)
        # Press home the first time. This should move to the beginning of the
        # indent: line 0, column 4.
        self.assertEqual(self.qpart.cursorPosition, (0, 4))

    def column(self):
        """ Return the column at which the cursor is located."""
        return self.qpart.cursorPosition[1]

    def test_home2(self):
        """ Test the operation of the home key. """

        self.qpart.show()
        self.qpart.text = '\n\n    ' + 'x'*10000
        # Move to the end of this string.
        self.qpart.cursorPosition = (100, 100)
        # Press home. We should either move to the line beginning or indent.
        QTest.keyClick(self.qpart, Qt.Key_Home)
        # There's no way I can find of determine what the line beginning should
        # be. So, just press home again if we're not at the indent.
        if self.column() != 4:
            # Press home again to move to the beginning of the indent.
            QTest.keyClick(self.qpart, Qt.Key_Home)
        # We're at the indent.
        self.assertEqual(self.column(), 4)

        # Move to the beginning of the line.
        QTest.keyClick(self.qpart, Qt.Key_Home)
        self.assertEqual(self.column(), 0)

        # Move back to the beginning of the indent.
        QTest.keyClick(self.qpart, Qt.Key_Home)
        self.assertEqual(self.column(), 4)


if __name__ == '__main__':
    unittest.main()
