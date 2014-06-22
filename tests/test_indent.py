#!/usr/bin/env python3

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

    def test_1(self):
        # Indent with Tab
        self.qpart.indentUseTabs = True
        self.qpart.text = 'ab\ncd'
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'ab\n\tcd')

        self.qpart.indentUseTabs = False
        QTest.keyClick(self.qpart, Qt.Key_Backspace)
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'ab\n    cd')

    def test_2(self):
        # Unindent Tab
        self.qpart.indentUseTabs = True
        self.qpart.text = 'ab\n\t\tcd'
        self.qpart.cursorPosition = (1, 2)

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab\n\tcd')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab\ncd')

    def test_3(self):
        # Unindent Spaces
        self.qpart.indentUseTabs = False

        self.qpart.text = 'ab\n      cd'
        self.qpart.cursorPosition = (1, 6)

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab\n  cd')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab\ncd')

    def test_4(self):
        # (Un)indent multiline with Tab
        self.qpart.indentUseTabs = False

        self.qpart.text = '  ab\n  cd'
        self.qpart.selectedPosition = ((0, 2), (1, 3))

        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, '      ab\n      cd')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, '  ab\n  cd')

    def test_5(self):
        # (Un)indent multiline with Space
        self.qpart.indentUseTabs = False

        self.qpart.text = '  ab\n  cd'
        self.qpart.selectedPosition = ((0, 2), (1, 3))

        QTest.keyClick(self.qpart, Qt.Key_Space, Qt.ShiftModifier)
        self.assertEqual(self.qpart.text, '   ab\n   cd')

        QTest.keyClick(self.qpart, Qt.Key_Backspace, Qt.ShiftModifier)
        self.assertEqual(self.qpart.text, '  ab\n  cd')

    def test_6(self):
        # (Unindent Tab/Space mix
        self.qpart.indentUseTabs = False

        self.qpart.text = '    \t  \tab'
        self.qpart.cursorPosition = ((0, 8))

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, '    \t  ab')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, '    \tab')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, '    ab')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab')

        self.qpart.decreaseIndentAction.trigger()
        self.assertEqual(self.qpart.text, 'ab')

    def test_7(self):
        """Smartly indent python"""
        self.qpart.detectSyntax(language='Python')

        QTest.keyClicks(self.qpart, "def main():")
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.cursorPosition, (1, 4))

        QTest.keyClicks(self.qpart, "return 7")
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.cursorPosition, (2, 0))


if __name__ == '__main__':
    unittest.main()
