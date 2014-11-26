#!/usr/bin/env python
# encoding: utf8


import os
import sys
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

    def tearDown(self):
        self.qpart.hide()
        del self.qpart


class Test(_Test):
    def test_01(self):
        """Switch modes insert/normal
        """
        QTest.keyClicks(self.qpart, "i123")
        QTest.keyClick(self.qpart, Qt.Key_Escape)
        QTest.keyClicks(self.qpart, "i4")
        self.assertEqual(self.qpart.lines[0],
                         '1234The quick brown fox')

    def test_02(self):
        """Append with A
        """
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "A")
        QTest.keyClicks(self.qpart, "XY")

        self.assertEqual(self.qpart.lines[2],
                         'lazy dogXY')


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
        self.qpart.lines[0] = 'word, comma, word'
        self.qpart.cursorPosition = (0, 0)
        for column in (4, 6, 11, 13, 17, 0):
            QTest.keyClick(self.qpart, 'w')
            self.assertEqual(self.qpart.cursorPosition[1], column)

        self.assertEqual(self.qpart.cursorPosition, (1, 0))


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
