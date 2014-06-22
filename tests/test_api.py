#!/usr/bin/env python3

import os
import sys
import unittest

import base

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from qutepart import Qutepart

import qutepart.completer
qutepart.completer._GlobalUpdateWordSetTimer._IDLE_TIMEOUT_MS = 0

class _BaseTest(unittest.TestCase):
    """Base class for tests
    """
    app = base.papp  # app crashes, if created more than once

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

    def test_setSelection(self):
        self.qpart.text = 'asdf fdsa'

        self.qpart.selectedPosition = ((0, 3), (0, 7))

        self.assertEqual(self.qpart.selectedText, "f fd")
        self.assertEqual(self.qpart.selectedPosition, ((0, 3), (0, 7)))

    def test_selected_multiline_text(self):
        self.qpart.text = "a\nb"
        self.qpart.selectedPosition = ((0, 0), (1, 1))
        self.assertEqual(self.qpart.selectedText, "a\nb")

class ReplaceText(_BaseTest):
    def test_replaceText1(self):
        # Basic case
        self.qpart.text = '123456789'
        self.qpart.replaceText(3, 4, 'xyz')
        self.assertEqual(self.qpart.text, '123xyz89')

    def test_replaceText2(self):
        # Replace uses (line, col) position
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((1, 4), 3, 'Z')
        self.assertEqual(self.qpart.text, '12345\n6789Zbcde')

    def test_replaceText3(self):
        # Edge cases
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((0, 0), 3, 'Z')
        self.assertEqual(self.qpart.text, 'Z45\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((2, 4), 1, 'Z')
        self.assertEqual(self.qpart.text, '12345\n67890\nabcdZ')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((0, 0), 0, 'Z')
        self.assertEqual(self.qpart.text, 'Z12345\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText((2, 5), 0, 'Z')
        self.assertEqual(self.qpart.text, '12345\n67890\nabcdeZ')

    def test_replaceText4(self):
        # Replace nothing with something
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.replaceText(2, 0, 'XYZ')
        self.assertEqual(self.qpart.text, '12XYZ345\n67890\nabcde')

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
        self.assertEqual(self.qpart.text, '123xyz456789')

    def test_2(self):
        # (line, col) position
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((1, 4), 'Z')
        self.assertEqual(self.qpart.text, '12345\n6789Z0\nabcde')

    def test_3(self):
        # Edge cases
        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((0, 0), 'Z')
        self.assertEqual(self.qpart.text, 'Z12345\n67890\nabcde')

        self.qpart.text = '12345\n67890\nabcde'
        self.qpart.insertText((2, 5), 'Z')
        self.assertEqual(self.qpart.text, '12345\n67890\nabcdeZ')


class IsCodeOrComment(_BaseTest):
    def _wait_highlighting_finished(self):
        base._processPendingEvents(self.app)

    def test_1(self):
        # Basic case
        self.qpart.text = 'a + b # comment'
        self.qpart.detectSyntax(language = 'Python')
        self._wait_highlighting_finished()
        self.assertEqual([self.qpart.isCode(0, i) for i in range(len(self.qpart.text))],
                          [True, True, True, True, True, True, False, False, False, False, \
                           False, False, False, False, False])
        self.assertEqual([self.qpart.isComment(0, i) for i in range(len(self.qpart.text))],
                          [False, False, False, False, False, False, True, True, True, True, \
                          True, True, True, True, True])

    def test_2(self):
        self.qpart.text = '#'
        self.qpart.detectSyntax(language = 'Python')
        self._wait_highlighting_finished()

        self.assertFalse(self.qpart.isCode(0, 0))
        self.assertTrue(self.qpart.isComment(0, 0))
        self.assertFalse(self.qpart.isBlockComment(0, 0))

    def test_block_comment(self):
        self.qpart.text = 'if foo\n=begin xxx'
        self.qpart.detectSyntax(language = 'Ruby')
        self._wait_highlighting_finished()

        self.assertFalse(self.qpart.isBlockComment(0, 3))
        self.assertTrue(self.qpart.isBlockComment(1, 8))
        self.assertTrue(self.qpart.isComment(1, 8))

    def test_here_doc(self):
        self.qpart.text = "doc = <<EOF\nkoko"
        self.qpart.detectSyntax(language = 'Ruby')

        self._wait_highlighting_finished()

        self.assertFalse(self.qpart.isHereDoc(0, 3))
        self.assertTrue(self.qpart.isHereDoc(1, 2))
        self.assertTrue(self.qpart.isComment(1, 2))


class DetectSyntax(_BaseTest):
    def test_1(self):
        self.qpart.detectSyntax(xmlFileName='ada.xml')
        self.assertEqual(self.qpart.language(), 'Ada')

        self.qpart.detectSyntax(mimeType='text/x-cgsrc')
        self.assertEqual(self.qpart.language(), 'Cg')

        self.qpart.detectSyntax(language='CSS')
        self.assertEqual(self.qpart.language(), 'CSS')

        self.qpart.detectSyntax(sourceFilePath='/tmp/file.feh')
        self.assertEqual(self.qpart.language(), 'ferite')

        self.qpart.detectSyntax(firstLine='<?php hello() ?>')
        self.assertEqual(self.qpart.language(), 'PHP (HTML)')


class Signals(_BaseTest):
    def test_language_changed(self):
        newValue = [None]
        def setNeVal(val):
            newValue[0] = val
        self.qpart.languageChanged.connect(setNeVal)

        self.qpart.detectSyntax(language='Python')
        self.assertEqual(newValue[0], 'Python')

    def test_indent_width_changed(self):
        newValue = [None]
        def setNeVal(val):
            newValue[0] = val
        self.qpart.indentWidthChanged.connect(setNeVal)

        self.qpart.indentWidth = 7
        self.assertEqual(newValue[0], 7)

    def test_use_tabs_changed(self):
        newValue = [None]
        def setNeVal(val):
            newValue[0] = val

        self.qpart.indentUseTabsChanged.connect(setNeVal)

        self.qpart.indentUseTabs = True
        self.assertEqual(newValue[0], True)

    def test_eol_changed(self):
        newValue = [None]
        def setNeVal(val):
            newValue[0] = val

        self.qpart.eolChanged.connect(setNeVal)

        self.qpart.eol = '\r\n'
        self.assertEqual(newValue[0], '\r\n')


class Completion(_BaseTest):
    def _assertVisible(self):
        self.assertTrue(self.qpart._completer._widget is not None)

    def _assertNotVisible(self):
        self.assertTrue(self.qpart._completer._widget is None)

    def setUp(self):
        super(Completion, self).setUp()
        self.qpart.text = 'completableWord\n'
        self.qpart.cursorPosition = (1, 0)
        base._processPendingEvents(self.app)

    def test_completion_enabled(self):
        self._assertNotVisible()

        self.qpart.completionEnabled = True
        QTest.keyClicks(self.qpart, "comple")
        self._assertVisible()

        for i in range(len('comple')):
            QTest.keyClick(self.qpart, Qt.Key_Backspace)
        self._assertNotVisible()

        self.qpart.completionEnabled = False
        QTest.keyClicks(self.qpart, "comple")
        self._assertNotVisible()

    def test_threshold(self):
        self._assertNotVisible()

        self.qpart.completionThreshold = 8
        QTest.keyClicks(self.qpart, "complet")
        self._assertNotVisible()

        QTest.keyClicks(self.qpart, "a")
        self._assertVisible()


class Lines(_BaseTest):
    def setUp(self):
        super(Lines, self).setUp()
        self.qpart.text = 'abcd\nefgh\nklmn\nopqr'

    def test_accessByIndex(self):
        self.assertEqual(self.qpart.lines[0], 'abcd')
        self.assertEqual(self.qpart.lines[1], 'efgh')
        self.assertEqual(self.qpart.lines[-1], 'opqr')

    def test_modifyByIndex(self):
        self.qpart.lines[2] = 'new text'
        self.assertEqual(self.qpart.text, 'abcd\nefgh\nnew text\nopqr')

    def test_getSlice(self):
        self.assertEqual(self.qpart.lines[0], 'abcd')
        self.assertEqual(self.qpart.lines[1], 'efgh')
        self.assertEqual(self.qpart.lines[3], 'opqr')
        self.assertEqual(self.qpart.lines[-4], 'abcd')
        self.assertEqual(self.qpart.lines[1:4], ['efgh', 'klmn', 'opqr'])
        self.assertEqual(self.qpart.lines[1:7], ['efgh', 'klmn', 'opqr'])  # Python list behaves this way
        self.assertEqual(self.qpart.lines[0:0], [])
        self.assertEqual(self.qpart.lines[0:1], ['abcd'])
        self.assertEqual(self.qpart.lines[:2], ['abcd', 'efgh'])
        self.assertEqual(self.qpart.lines[0:-2], ['abcd', 'efgh'])
        self.assertEqual(self.qpart.lines[-2:], ['klmn', 'opqr'])
        self.assertEqual(self.qpart.lines[-4:-2], ['abcd', 'efgh'])

        with self.assertRaises(IndexError):
            self.qpart.lines[4]
        with self.assertRaises(IndexError):
            self.qpart.lines[-5]

    def test_setSlice_1(self):
        self.qpart.lines[0] = 'xyz'
        self.assertEqual(self.qpart.text, 'xyz\nefgh\nklmn\nopqr')

    def test_setSlice_2(self):
        self.qpart.lines[1] = 'xyz'
        self.assertEqual(self.qpart.text, 'abcd\nxyz\nklmn\nopqr')

    def test_setSlice_3(self):
        self.qpart.lines[-4] = 'xyz'
        self.assertEqual(self.qpart.text, 'xyz\nefgh\nklmn\nopqr')

    def test_setSlice_4(self):
        self.qpart.lines[0:4] = ['st', 'uv', 'wx', 'z']
        self.assertEqual(self.qpart.text, 'st\nuv\nwx\nz')

    def test_setSlice_5(self):
        self.qpart.lines[0:47] = ['st', 'uv', 'wx', 'z']
        self.assertEqual(self.qpart.text, 'st\nuv\nwx\nz')

    def test_setSlice_6(self):
        self.qpart.lines[1:3] = ['st', 'uv']
        self.assertEqual(self.qpart.text, 'abcd\nst\nuv\nopqr')

    def test_setSlice_61(self):
        with self.assertRaises(ValueError):
            self.qpart.lines[1:3] = ['st', 'uv', 'wx', 'z']

    def test_setSlice_7(self):
        self.qpart.lines[-3:3] = ['st', 'uv']
        self.assertEqual(self.qpart.text, 'abcd\nst\nuv\nopqr')

    def test_setSlice_8(self):
        self.qpart.lines[-3:-1] = ['st', 'uv']
        self.assertEqual(self.qpart.text, 'abcd\nst\nuv\nopqr')

    def test_setSlice_9(self):
        with self.assertRaises(IndexError):
            self.qpart.lines[4] = 'st'
        with self.assertRaises(IndexError):
            self.qpart.lines[-5] = 'st'


class LinesWin(Lines):
    def setUp(self):
        super(LinesWin, self).setUp()
        self.qpart.eol = '\r\n'

if __name__ == '__main__':
    unittest.main()
