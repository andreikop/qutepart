#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))
from qutepart import Qutepart

class Test(unittest.TestCase):
    """Base class for tests
    """
    app = QApplication(sys.argv)  # app crashes, if created more than once
    
    def setUp(self):
        self.qpart = Qutepart()
    
    def tearDown(self):
        del self.qpart

    def test_real_to_visible(self):
        self.qpart.text = 'abcdfg'
        self.assertEqual(0, self.qpart._realToVisibleColumn(self.qpart.text, 0))
        self.assertEqual(2, self.qpart._realToVisibleColumn(self.qpart.text, 2))
        self.assertEqual(6, self.qpart._realToVisibleColumn(self.qpart.text, 6))
        
        self.qpart.text = '\tab\tcde\t'
        self.assertEqual(0, self.qpart._realToVisibleColumn(self.qpart.text, 0))
        self.assertEqual(4, self.qpart._realToVisibleColumn(self.qpart.text, 1))
        self.assertEqual(5, self.qpart._realToVisibleColumn(self.qpart.text, 2))
        self.assertEqual(8, self.qpart._realToVisibleColumn(self.qpart.text, 4))
        self.assertEqual(12, self.qpart._realToVisibleColumn(self.qpart.text, 8))

    def test_visible_to_real(self):
        self.qpart.text = 'abcdfg'
        self.assertEqual(0, self.qpart._visibleToRealColumn(self.qpart.text, 0))
        self.assertEqual(2, self.qpart._visibleToRealColumn(self.qpart.text, 2))
        self.assertEqual(6, self.qpart._visibleToRealColumn(self.qpart.text, 6))
        
        self.qpart.text = '\tab\tcde\t'
        self.assertEqual(0, self.qpart._visibleToRealColumn(self.qpart.text, 0))
        self.assertEqual(1, self.qpart._visibleToRealColumn(self.qpart.text, 4))
        self.assertEqual(2, self.qpart._visibleToRealColumn(self.qpart.text, 5))
        self.assertEqual(4, self.qpart._visibleToRealColumn(self.qpart.text, 8))
        self.assertEqual(8, self.qpart._visibleToRealColumn(self.qpart.text, 12))
        
        self.assertEqual(None, self.qpart._visibleToRealColumn(self.qpart.text, 13))


if __name__ == '__main__':
    unittest.main()
