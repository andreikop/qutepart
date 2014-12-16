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
        """Append with a
        """
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "a")
        self.assertEqual(self.vimMode, 'insert')
        QTest.keyClicks(self.qpart, "XY")

        self.assertEqual(self.qpart.lines[2],
                         'lXYazy dog')


    def test_04(self):
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

    def test_06(self):
        """G
        """
        self.qpart.cursorPosition = (0, 10)
        QTest.keyClick(self.qpart, 'G')
        self.assertEqual(self.qpart.cursorPosition, (3, 4))

    def test_07(self):
        """gg
        """
        self.qpart.cursorPosition = (2, 10)
        QTest.keyClicks(self.qpart, 'gg')
        self.assertEqual(self.qpart.cursorPosition, (00, 0))



class Del(_Test):
    def test_01a(self):
        """Delete with x
        """
        self.qpart.cursorPosition = (0, 4)
        QTest.keyClicks(self.qpart, "xxxxx")

        self.assertEqual(self.qpart.lines[0],
                         'The  brown fox')
        self.assertEqual(self.qpart._vim.internalClipboard, 'k')

    def test_01b(self):
        """Delete with x
        """
        self.qpart.cursorPosition = (0, 4)
        QTest.keyClicks(self.qpart, "5x")

        self.assertEqual(self.qpart.lines[0],
                         'The  brown fox')
        self.assertEqual(self.qpart._vim.internalClipboard, 'quick')

    def test_02(self):
        """Composite delete with d. Left and right
        """
        self.qpart.cursorPosition = (1, 1)
        QTest.keyClicks(self.qpart, "dl")
        self.assertEqual(self.qpart.lines[1],
                         'jmps over the')

        QTest.keyClicks(self.qpart, "dh")
        self.assertEqual(self.qpart.lines[1],
                         'mps over the')

    def test_03(self):
        """Composite delete with d. Down
        """
        self.qpart.cursorPosition = (0, 2)
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         ['lazy dog',
                          'back'])
        self.assertEqual(self.qpart.cursorPosition[1], 0)

        # nothing deleted, if having only one line
        self.qpart.cursorPosition = (1, 1)
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         ['lazy dog',
                          'back'])


        QTest.keyClicks(self.qpart, 'k')
        QTest.keyClicks(self.qpart, 'dj')
        self.assertEqual(self.qpart.lines[:],
                         [''])
        self.assertEqual(self.qpart._vim.internalClipboard,
                         ['lazy dog',
                          'back'])

    def test_04(self):
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
        self.assertEqual(self.qpart._vim.internalClipboard,
                         ['jumps over the',
                          'lazy dog'])

        self.assertEqual(self.qpart.cursorPosition[1], 0)

    def test_05(self):
        """Delete Count times
        """
        QTest.keyClicks(self.qpart, '3dw')
        self.assertEqual(self.qpart.lines[0], 'fox')
        self.assertEqual(self.qpart._vim.internalClipboard,
                         'The quick brown ')

    def test_06(self):
        """Delete line
        dd
        """
        self.qpart.cursorPosition = (1, 0)
        QTest.keyClicks(self.qpart, 'dd')
        self.assertEqual(self.qpart.lines[:],
                         ['The quick brown fox',
                          'lazy dog',
                          'back'])

    def test_07(self):
        """Delete until end of file
        G
        """
        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, 'dG')
        self.assertEqual(self.qpart.lines[:],
                         ['The quick brown fox',
                          'jumps over the'])

    def test_08(self):
        """Delete until start of file
        gg
        """
        self.qpart.cursorPosition = (1, 0)
        QTest.keyClicks(self.qpart, 'dgg')
        self.assertEqual(self.qpart.lines[:],
                         ['lazy dog',
                          'back'])



class Edit(_Test):
    def test_01(self):
        """Undo
        """
        oldText = self.qpart.text
        QTest.keyClicks(self.qpart, 'ddu')
        self.assertEqual(self.qpart.text, oldText)

    def test_02(self):
        """Paste text with p
        """
        self.qpart.cursorPosition = (0, 4)
        QTest.keyClicks(self.qpart, "5x")
        self.assertEqual(self.qpart.lines[0],
                         'The  brown fox')

        QTest.keyClicks(self.qpart, "p")
        self.assertEqual(self.qpart.lines[0],
                         'The quick brown fox')  # NOTE 'The  quickbrown fox' in vim

    def test_03(self):
        """Paste lines with p
        """
        self.qpart.cursorPosition = (1, 2)
        QTest.keyClicks(self.qpart, "2dd")
        self.assertEqual(self.qpart.lines[:],
                         ['The quick brown fox',
                          'back'])

        QTest.keyClicks(self.qpart, "kkk")
        QTest.keyClicks(self.qpart, "p")
        self.assertEqual(self.qpart.lines[:],
                         ['The quick brown fox',
                          'jumps over the',
                          'lazy dog',
                          'back'])

    def test_04(self):
        """Replace char with r
        """
        self.qpart.cursorPosition = (0, 4)
        QTest.keyClicks(self.qpart, 'rZ')
        self.assertEqual(self.qpart.lines[0],
                         'The Zuick brown fox')

        QTest.keyClicks(self.qpart, 'rW')
        self.assertEqual(self.qpart.lines[0],
                         'The Wuick brown fox')

    def test_05(self):
        """Change 2 words with c
        """
        QTest.keyClicks(self.qpart, 'c2e')
        QTest.keyClicks(self.qpart, 'asdf')
        self.assertEqual(self.qpart.lines[0],
                         'asdf brown fox')


if __name__ == '__main__':
    unittest.main()
