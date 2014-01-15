#!/usr/bin/env python

import os
import sys
import unittest

import base

from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt, QTimer

from qutepart import Qutepart

class _BaseTest(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

    def setUp(self):
        self.qpart = Qutepart()

    def tearDown(self):
        del self.qpart


class Print(_BaseTest):
    def _rm(self):
        try:
            os.remove('print.pdf')
        except:
            pass

    def _exists(self):
        return os.path.isfile('print.pdf')

    @unittest.skipUnless(sys.platform.startswith("linux"), "Works only on Linux")
    def test_1(self):
        self._rm()
        self.assertFalse(self._exists())
        self.qpart.show()
        def acceptDialog():
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Enter, Qt.NoModifier)
        QTimer.singleShot(1000, acceptDialog)
        QTest.keyClick(self.qpart, Qt.Key_P, Qt.ControlModifier)

        self.assertTrue(self._exists())
        self._rm()


if __name__ == '__main__':
    unittest.main()
