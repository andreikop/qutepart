#!/usr/bin/env python3

import os
import sys
import unittest

import base

from PyQt4.QtCore import Qt, QTimer, QPoint
from PyQt4.QtTest import QTest


from qutepart import Qutepart, iterateBlocksFrom



class Test(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

    def setUp(self):
        self.qpart = Qutepart()

    def tearDown(self):
        del self.qpart

    def _markedBlocks(self):
        bookMarksObject = self.qpart._bookmarks
        return [block.blockNumber() \
                    for block in iterateBlocksFrom(self.qpart.document().firstBlock()) \
                        if bookMarksObject.isBlockMarked(block)]

    @base.in_main_loop
    def test_set_with_keyboard(self):
        self.qpart.text = '\n' * 5
        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        self.assertEqual(self._markedBlocks(), [0, 2])

        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        self.assertEqual(self._markedBlocks(), [0])

    @unittest.skip('Crashes Qt')
    @base.in_main_loop
    def test_set_with_mouse(self):
        self.qpart.text = '\n' * 5

        secondBlock = self.qpart.document().findBlockByNumber(2)
        geometry = self.qpart.blockBoundingGeometry(secondBlock).translated(self.qpart.contentOffset())

        QTest.mouseClick(self.qpart._markArea, Qt.LeftButton, Qt.NoModifier, QPoint(0, geometry.bottom() - 1))
        self.assertEqual(self._markedBlocks(), [1])

    @base.in_main_loop
    def test_jump(self):
        self.qpart.text = '\n' * 5
        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        for i in range(2):
            QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        for i in range(2):
            QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_B, Qt.ControlModifier)
        self.assertEqual(self._markedBlocks(), [0, 2, 4])

        self.qpart.cursorPosition = (0, 0)

        QTest.keyClick(self.qpart, Qt.Key_PageDown, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 2)
        QTest.keyClick(self.qpart, Qt.Key_PageDown, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 4)
        QTest.keyClick(self.qpart, Qt.Key_PageDown, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 4)

        QTest.keyClick(self.qpart, Qt.Key_PageUp, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 2)
        QTest.keyClick(self.qpart, Qt.Key_PageUp, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 0)
        QTest.keyClick(self.qpart, Qt.Key_PageUp, Qt.AltModifier)
        self.assertEqual(self.qpart.cursorPosition[0], 0)


if __name__ == '__main__':
    unittest.main()
