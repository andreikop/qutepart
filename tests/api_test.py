#!/usr/bin/env python

import os
import sys
import unittest

import sip
sip.setapi('QString', 2)

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

class Selection(_BaseTest):
    
    def test_resetSelection(self):
        # Reset selection
        self.qpart.text = 'asdf fdsa'
        self.qpart.absSelectedPosition = 1, 3
        self.assertTrue(self.qpart.textCursor().hasSelection())
        self.qpart.resetSelection()
        self.assertFalse(self.qpart.textCursor().hasSelection())

class ReplaceText(_BaseTest):
    def test_replaceText1(self):
        # Basic case
        self.qpart.text = '123456789'
        self.qpart.replaceText(3, 4, 'xyz')
        self.assertEquals(self.qpart.text, '123xyz89')

    def test_replaceText2(self):
        # Replace uses (line, col) position
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((1, 4), 3, 'Z')
        self.assertEquals(self.qpart.text, '12345\n6789Zbcde')

    def test_replaceText3(self):
        # Edge cases
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((0, 0), 3, 'Z')
        self.assertEquals(self.qpart.text, 'Z45\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((2, 4), 1, 'Z')
        self.assertEquals(self.qpart.text, '12345\n67890\nabcdZ')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((0, 0), 0, 'Z')
        self.assertEquals(self.qpart.text, 'Z12345\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((2, 5), 0, 'Z')
        self.assertEquals(self.qpart.text, '12345\n67890\nabcdeZ')

    def test_replaceText4(self):
        # Replace nothing with something
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText(2, 0, 'XYZ')
        self.assertEquals(self.qpart.text, '12XYZ345\n67890\nabcde')

    def test_replaceText5(self):
        # Make sure exceptions are raised for invalid params
        self.qpart.text = '12345\n67890\nabcde'
        self.assertRaises(IndexError, self.qpart.replaceText, -1, 1, 'Z')
        self.assertRaises(IndexError, self.qpart.replaceText, len(self.qpart.text) + 1, 0, 'Z')
        self.assertRaises(IndexError, self.qpart.replaceText, len(self.qpart.text), 1, 'Z')
        self.assertRaises(IndexError, self.qpart.replaceText, (0, 7), 1, 'Z')
        self.assertRaises(IndexError, self.qpart.replaceText, (7, 0), 1, 'Z')


class InsertText(_BaseTest):
    def test_1(self):
        # Basic case
        self.qpart.text = '123456789'
        self.qpart.insertText(3, 'xyz')
        self.assertEquals(self.qpart.text, '123xyz456789')

    def test_2(self):
        # (line, col) position
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((1, 4), 'Z')
        self.assertEquals(self.qpart.text, '12345\n6789Z0\nabcde')

    def test_3(self):
        # Edge cases
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((0, 0), 'Z')
        self.assertEquals(self.qpart.text, 'Z12345\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((2, 5), 'Z')
        self.assertEquals(self.qpart.text, '12345\n67890\nabcdeZ')


class IsCodeOrComment(_BaseTest):
    def test_1(self):
        # Basic case
        self.qpart.text = 'a + b # comment'
        self.qpart.detectSyntax(language = 'Python')
        self.assertEquals([self.qpart.isCode(0, i) for i in range(len(self.qpart.text))],
                          [True, True, True, True, True, True, False, False, False, False, \
                           False, False, False, False, False])
        self.assertEquals([self.qpart.isComment(0, i) for i in range(len(self.qpart.text))],
                          [False, False, False, False, False, False, True, True, True, True, \
                          True, True, True, True, True])

    def test_2(self):
        self.qpart.text = '#'
        self.qpart.detectSyntax(language = 'Python')
        self.assertFalse(self.qpart.isCode(0, 0))
        self.assertTrue(self.qpart.isComment(0, 0))


if __name__ == '__main__':
    unittest.main()
