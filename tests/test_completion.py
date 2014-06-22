#!/usr/bin/env python3

import os
import sys
import unittest

import base

from PyQt4.QtCore import Qt, QPoint
from PyQt4.QtGui import QMainWindow
from PyQt4.QtTest import QTest

from qutepart import Qutepart
import qutepart.completer
qutepart.completer._GlobalUpdateWordSetTimer._IDLE_TIMEOUT_MS = 0


class Test(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

    def setUp(self):
        self._window = QMainWindow()
        self.qpart = Qutepart()
        self._window.setCentralWidget(self.qpart)
        self._window.menuBar().addAction(self.qpart.invokeCompletionAction)

    def tearDown(self):
        del self.qpart

    def test_down_selects_first(self):
        self.qpart.text = 'aaaa\nbbbb\ncccX\ndddd\ncccY'

        while self.app.hasPendingEvents():
            self.app.processEvents()

        QTest.keyClicks(self.qpart, "ccc")
        QTest.keyClick(self.qpart, Qt.Key_Down)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        QTest.keyClick(self.qpart, Qt.Key_Enter)
        self.assertEqual(self.qpart.text, 'cccX\naaaa\nbbbb\ncccX\ndddd\ncccY')

    def test_down_selects_second(self):
        self.qpart.text = 'aaaa\nbbbb\ncccX\ndddd\ncccY'

        base._processPendingEvents(self.app)

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

        base._processPendingEvents(self.app)

        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "aaa")
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaa')
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaaXXXXX')

    def test_manual(self):
        self._window.show()

        self.qpart.text = 'aaaaa\naaaaaXXXXX\n'

        base._processPendingEvents(self.app)

        self.qpart.cursorPosition = (2, 0)
        QTest.keyClicks(self.qpart, "a")

        QTest.keyPress(self.qpart, Qt.Key_Space, Qt.ControlModifier, 100)

        QTest.keyClicks(self.qpart, "a")
        QTest.keyClick(self.qpart, Qt.Key_Tab)
        self.assertEqual(self.qpart.text, 'aaaaa\naaaaaXXXXX\naaaaa')

    @base.in_main_loop
    def test_too_long_list(self):
        self._window.show()

        self.qpart.text = '\n'.join(['asdf' + str(i) \
                                        for i in range(100)]) + '\n'
        base._processPendingEvents(self.app)
        self.qpart.cursorPosition = (100, 0)
        QTest.keyClicks(self.qpart, "asdf")
        self.assertIsNotNone(self.qpart._completer._widget)

        self.qpart.text = '\n'.join(['asdf' + str(i) \
                                        for i in range(1000)]) + '\n'
        base._processPendingEvents(self.app)
        self.qpart.cursorPosition = (1000, 0)
        QTest.keyClicks(self.qpart, "asdf")
        self.assertIsNone(self.qpart._completer._widget)

        QTest.keyPress(self.qpart, Qt.Key_Space, Qt.ControlModifier, 100)
        self.assertIsNotNone(self.qpart._completer._widget)


if __name__ == '__main__':
    unittest.main()
