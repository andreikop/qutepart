#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))
from qutepart import Qutepart

class _BaseTest(unittest.TestCase):
    """Base class for tests
    """
    app = QApplication(sys.argv)  # app crashes, if created more than once
    
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
    
    def test_1(self):
        self._rm()
        self.assertFalse(self._exists())
        self.qpart.show()
        def acceptDialog():
            QTest.keyClick(self.app.focusWidget(), Qt.Key_Enter, Qt.NoModifier)
        QTimer.singleShot(600, acceptDialog)
        QTest.keyClick(self.qpart, Qt.Key_P, Qt.ControlModifier, 100)
        
        self.assertTrue(self._exists())
        self._rm()


if __name__ == '__main__':
    unittest.main()
