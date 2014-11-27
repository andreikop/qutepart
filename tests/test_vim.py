#!/usr/bin/env python
# encoding: utf8


import unittest

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from qutepart import Qutepart


class _Test(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

    def setUp(self):
        self.qpart = Qutepart()
        self.qpart.lines = ['The quick brown fox',
                            'jumps over the',
                            'lazy dog',
                            'back']
        self.qpart.vimModeIndicationChanged.connect(self._onVimModeChanged)

        self.vimMode = 'normal'

    def tearDown(self):
        self.qpart.hide()
        del self.qpart

    def _onVimModeChanged(self, color, mode):
        self.vimMode = mode


class Modes(_Test):
    def test_01(self):
        """Switch modes insert/normal
        """
        self.assertEqual(self.vimMode, 'normal')
        QTest.keyClicks(self.qpart, "i123")
        self.assertEqual(self.vimMode, 'insert')
        QTest.keyClick(self.qpart, Qt.Key_Escape)
        self.assertEqual(self.vimMode, 'normal')
        QTest.keyClicks(self.qpart, "i4")
        self.assertEqual(self.vimMode, 'insert')
        self.assertEqual(self.qpart.lines[0],
                         '1234The quick brown fox')

    def test_02(self):
        """Append with A
        """
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "A")
        self.assertEqual(self.vimMode, 'insert')
        QTest.keyClicks(self.qpart, "XY")

        self.assertEqual(self.qpart.lines[2],
                         'lazy dogXY')

    def test_03(self):
        """Mode line shows composite command start
        """
        self.assertEqual(self.vimMode, 'normal')
        QTest.keyClick(self.qpart, 'd')
        self.assertEqual(self.vimMode, 'd')
        QTest.keyClick(self.qpart, 'w')
        self.assertEqual(self.vimMode, 'normal')



class Move(_Test):
    def test_01(self):
        """Move hjkl
        """
        QTest.keyClicks(self.qpart, "ll")
        self.assertEqual(self.qpart.cursorPosition, (0, 2))

        QTest.keyClicks(self.qpart, "jjj")
        self.assertEqual(self.qpart.cursorPosition, (3, 2))

        QTest.keyClicks(self.qpart, "h")
        self.assertEqual(self.qpart.cursorPosition, (3, 1))

        QTest.keyClicks(self.qpart, "k")
        self.assertEqual(self.qpart.cursorPosition, (2, 1))

    def test_02(self):
        """w
        """
        self.qpart.lines[0] = 'word, comma, word'
        self.qpart.cursorPosition = (0, 0)
        for column in (4, 6, 11, 13, 17, 0):
            QTest.keyClick(self.qpart, 'w')
            self.assertEqual(self.qpart.cursorPosition[1], column)

        self.assertEqual(self.qpart.cursorPosition, (1, 0))

    def test_03(self):
        """e
        """
        self.qpart.lines[0] = 'word, comma, word'
        self.qpart.cursorPosition = (0, 0)
        for column in (4, 5, 11, 12, 17, 5):
            QTest.keyClick(self.qpart, 'e')
            self.assertEqual(self.qpart.cursorPosition[1], column)

        self.assertEqual(self.qpart.cursorPosition, (1, 5))

    def test_04(self):
        """$
        """
        QTest.keyClick(self.qpart, '$')
        self.assertEqual(self.qpart.cursorPosition, (0, 19))
        QTest.keyClick(self.qpart, '$')
        self.assertEqual(self.qpart.cursorPosition, (0, 19))

    def test_05(self):
        """0
        """
        self.qpart.cursorPosition = (0, 10)
        QTest.keyClick(self.qpart, '0')
        self.assertEqual(self.qpart.cursorPosition, (0, 0))



class Del(_Test):
    def test_03(self):
        """Delete with x
        """
        self.qpart.cursorPosition = (0, 4)
        QTest.keyClicks(self.qpart, "xxxxx")

        self.assertEqual(self.qpart.lines[0],
                         'The  brown fox')

    def test_05(self):
        """Composite delete with d. Left and right
        """
        self.qpart.cursorPosition = (1, 1)
        QTest.keyClicks(self.qpart, "dl")
        self.assertEqual(self.qpart.lines[1],
                         'jmps over the')

        QTest.keyClicks(self.qpart, "dh")
        self.assertEqual(self.qpart.lines[1],
                         'mps over the')

    def test_06(self):
        """Composite delete with d. Down
        """
        self.qpart.cursorPosition = (0, 2)
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         ['lazy dog',
                          'back'])
        self.assertEqual(self.qpart.cursorPosition[1], 0)

        self.qpart.cursorPosition = (1, 1)
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         ['lazy dog',
                          'back'])

        QTest.keyClicks(self.qpart, 'k')
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         [''])

    def test_07(self):
        """Composite delete with d. Up
        """
        self.qpart.cursorPosition = (0, 2)
        QTest.keyClicks(self.qpart, 'dk')
        self.assertEqual(len(self.qpart.lines), 4)

        self.qpart.cursorPosition = (2, 1)
        QTest.keyClicks(self.qpart, 'dk')
        self.assertEqual(self.qpart.lines[:],
                         ['The quick brown fox',
                          'back'])
        self.assertEqual(self.qpart.cursorPosition[1], 0)


if __name__ == '__main__':
    unittest.main()
