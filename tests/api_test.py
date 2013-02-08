#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtGui import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qutepart import Qutepart

class Test(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.qpart = Qutepart()

    def test_resetSelection(self):
        self.qpart.text = 'asdf fdsa'
        self.qpart.absSelectedPosition = 1, 3
        self.assertTrue(self.qpart.textCursor().hasSelection())
        self.qpart.resetSelection()
        self.assertFalse(self.qpart.textCursor().hasSelection())

if __name__ == '__main__':
    unittest.main()
