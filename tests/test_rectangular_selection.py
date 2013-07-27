#!/usr/bin/env python
# encoding: utf8


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
        self.qpart.hide()
        del self.qpart

    def test_basic(self):
        self.qpart.show()
        for key in [Qt.Key_Delete, Qt.Key_Backspace]:
            self.qpart.text = 'abcd\nef\nghkl\nmnop'
            QTest.keyClick(self.qpart, Qt.Key_Right)
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
            QTest.keyClick(self.qpart, key)
            self.assertEqual(self.qpart.text, 'ad\ne\ngl\nmnop')

    def test_reset_by_move(self):
        self.qpart.show()
        self.qpart.text = 'abcd\nef\nghkl\nmnop'
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Left)
        QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self.assertEqual(self.qpart.text, 'abcd\nef\ngkl\nmnop')

    def test_reset_by_edit(self):
        self.qpart.show()
        self.qpart.text = 'abcd\nef\nghkl\nmnop'
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClicks(self.qpart, 'x')
        QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self.assertEqual(self.qpart.text, 'abcd\nef\nghkl\nmnop')
    
    def test_with_tabs(self):
        self.qpart.show()
        self.qpart.text = 'abcdefghhhhh\n\tklm\n\t\txyz'
        self.qpart.cursorPosition = (0, 6)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_Delete)
        self.assertEqual(self.qpart.text, 'abcdefhh\n\tkl\n\t\tz')
    
    def test_copy_paste(self):
        self.qpart.indentUseTabs = True
        self.qpart.show()
        self.qpart.text = 'xx 123 yy\n' + \
                          'xx 456 yy\n' + \
                          'xx 789 yy\n' + \
                          '\n' + \
                          'asdfghijlmn\n' + \
                          'x\t\n' + \
                          '\n' + \
                          '\t\t\n' + \
                          'end\n'
        self.qpart.cursorPosition = 0, 3
        for i in range(3):
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        for i in range(2):
            QTest.keyClick(self.qpart, Qt.Key_Down, Qt.AltModifier | Qt.ShiftModifier)
        
        QTest.keyClick(self.qpart, Qt.Key_C, Qt.ControlModifier)
        
        self.qpart.cursorPosition = 4, 10
        QTest.keyClick(self.qpart, Qt.Key_V, Qt.ControlModifier)
        
        self.assertEqual(self.qpart.text,
                         'xx 123 yy\nxx 456 yy\nxx 789 yy\n\nasdfghijlm123n\nx\t      456\n\t\t  789\n\t\t\nend\n')
        
    def test_copy_paste_utf8(self):
        self.qpart.show()
        self.qpart.text = u'фыва'
        #self.app.exec_()
        for i in range(3):
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_C, Qt.ControlModifier)
        
        QTest.keyClick(self.qpart, Qt.Key_Right)
        QTest.keyClick(self.qpart, Qt.Key_Space)
        QTest.keyClick(self.qpart, Qt.Key_V, Qt.ControlModifier)
        
        self.assertEqual(self.qpart.text,
                         u'фыва фыв')

    def test_paste_replace_selection(self):
        self.qpart.show()
        self.qpart.text = 'asdf'
        
        for i in range(4):
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_C, Qt.ControlModifier)
        
        QTest.keyClick(self.qpart, Qt.Key_End)
        QTest.keyClick(self.qpart, Qt.Key_Left, Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_V, Qt.ControlModifier)
        
        self.assertEqual(self.qpart.text,
                         'asdasdf')

    def test_paste_replace_rectangular_selection(self):
        self.qpart.show()
        self.qpart.text = 'asdf'
        
        for i in range(4):
            QTest.keyClick(self.qpart, Qt.Key_Right, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_C, Qt.ControlModifier)
        
        QTest.keyClick(self.qpart, Qt.Key_Left)
        QTest.keyClick(self.qpart, Qt.Key_Left, Qt.AltModifier | Qt.ShiftModifier)
        QTest.keyClick(self.qpart, Qt.Key_V, Qt.ControlModifier)
        
        self.assertEqual(self.qpart.text,
                         'asasdff')


if __name__ == '__main__':
    unittest.main()
