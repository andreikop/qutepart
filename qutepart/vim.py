import sys

from PyQt4.QtCore import Qt, pyqtSignal, QObject
from PyQt4.QtGui import QColor, QTextCursor


""" This magic code sets variables like _a and _A in the global scope
"""
thismodule = sys.modules[__name__]
for code in range(ord('a'), ord('z')):
    shortName = chr(code)
    longName = 'Key_' + shortName.upper()
    qtCode = getattr(Qt, longName)
    setattr(thismodule, '_' + shortName, qtCode)
    setattr(thismodule, '_' + shortName.upper(), Qt.ShiftModifier + qtCode)

_Dollar = Qt.Key_Dollar
_Esc = Qt.Key_Escape
_Insert = Qt.Key_Insert
_0 = Qt.Key_0

def code(ev):
    return int(ev.modifiers()) + ev.key()


NORMAL = 'normal'
INSERT = 'insert'
REPLACE_CHAR = 'replace character'

MODE_COLORS = {NORMAL: QColor('#33cc33'),
               INSERT: QColor('#ff9900'),
               REPLACE_CHAR: QColor('#ff3300')}


class Vim(QObject):
    """Vim mode implementation.
    Listens events and does actions
    """
    modeIndicationChanged = pyqtSignal(QColor, unicode)

    def __init__(self, qpart):
        QObject.__init__(self)
        self._qpart = qpart
        self._mode = Normal(self, qpart)
        self.internalClipboard = ''  # delete commands save text to this clipboard
        self.updateIndication()

    def indication(self):
        return self._mode.color, self._mode.text()

    def updateIndication(self):
        self.modeIndicationChanged.emit(*self.indication())

    def keyPressEvent(self, ev):
        """Check the event. Return True if processed and False otherwise
        """
        if ev.key() in (Qt.Key_Shift, Qt.Key_Control,
                        Qt.Key_Meta, Qt.Key_Alt,
                        Qt.Key_AltGr, Qt.Key_CapsLock,
                        Qt.Key_NumLock, Qt.Key_ScrollLock):
            return False  # ignore modifier pressing. Will process key pressing later

        return self._mode.keyPressEvent(ev)

    def setMode(self, mode):
        self._mode = mode
        self.updateIndication()



class Mode:
    color = None

    def __init__(self, vim, qpart):
        self._vim = vim
        self._qpart = qpart

    def text(self):
        return None

    def keyPressEvent(self, ev):
        pass

    def switchMode(self, modeClass, *args):
        mode = modeClass(self._vim, self._qpart, *args)
        self._vim.setMode(mode)

    def switchModeAndProcess(self, text, modeClass, *args):
        mode = modeClass(self._vim, self._qpart, *args)
        self._vim.setMode(mode)
        return mode.keyPressEvent(text)



class Insert(Mode):
    color = QColor('#ff9900')

    def text(self):
        return 'insert'

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape:
            self.switchMode(Normal)
            return True

        return False


class ReplaceChar(Mode):
    color = QColor('#ee7777')

    def text(self):
        return 'replace char'

    def keyPressEvent(self, ev):
        if ev.text():  # a char
            self._qpart.setOverwriteMode(False)
            line, col = self._qpart.cursorPosition
            if col > 0:
                self._qpart.cursorPosition = (line, col - 1)  # return the cursor back after replacement
            self.switchMode(Normal)
            return True
        else:
            self._qpart.setOverwriteMode(False)
            self.switchMode(Normal)
            return False


class Replace(Mode):
    color = QColor('#ee7777')

    def text(self):
        return 'replace'

    def keyPressEvent(self, ev):
        if ev.key() == _Insert:
            self._qpart.setOverwriteMode(False)
            self.switchMode(Insert)
            return True
        elif ev.key() == _Esc:
            self._qpart.setOverwriteMode(False)
            self.switchMode(Normal)
            return True
        else:
            return False


_MOTIONS = (_0, _e, _G, _j, _l, _k, _h, _w, _Dollar)

def _moveCursor(qpart, motion, select=False):
    """ Move cursor.
    Used by Normal and Visual mode
    """
    cursor = qpart.textCursor()

    moveMode = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor

    moveOperation = {_j: QTextCursor.Down,
                     _k: QTextCursor.Up,
                     _h: QTextCursor.Left,
                     _l: QTextCursor.Right,
                     _w: QTextCursor.WordRight,
                     _Dollar: QTextCursor.EndOfLine,
                     _0: QTextCursor.StartOfLine,
                     'gg': QTextCursor.Start,
                     _G: QTextCursor.End
                    }

    if motion in moveOperation:
        cursor.movePosition(moveOperation[motion], moveMode)
    elif motion == _e:
        oldPos = cursor.position()
        cursor.movePosition(QTextCursor.EndOfWord, moveMode)
        if cursor.position() == oldPos:
            cursor.movePosition(QTextCursor.Right, moveMode)
            cursor.movePosition(QTextCursor.EndOfWord, moveMode)

    qpart.setTextCursor(cursor)


class Visual(Mode):
    color = QColor('#6699ff')

    def __init__(self, *args):
        Mode.__init__(self, *args)
        self._reset()

    def _reset(self):
        self._processCharCoroutine = self._processChar()
        self._processCharCoroutine.next()  # run until the first yield
        self._typedText = ''

    def text(self):
        return self._typedText or 'visual'

    def keyPressEvent(self, ev):
        self._typedText += ev.text()
        try:
            self._processCharCoroutine.send(ev)
        except StopIteration as ex:
            retVal = ex.args[0]
            self._reset()
        else:
            retVal = True

        self._vim.updateIndication()

        return retVal

    def _processChar(self):
        ev = yield None

        # Get count
        count = 0

        if ev.key() != _0:
            char = ev.text()
            while char.isdigit():
                digit = int(char)
                count = (count * 10) + digit
                ev = yield
                char = ev.text()

        if count == 0:
            count = 1

        # Now get the action
        action = code(ev)
        if action in self._SIMPLE_COMMANDS:
            cmdFunc = self._SIMPLE_COMMANDS[action]
            self.switchMode(Normal)
            cmdFunc(self, action)
            raise StopIteration(True)
        elif action in _MOTIONS:
            for _ in range(count):
                _moveCursor(self._qpart, action, select=True)
            raise StopIteration(True)
        elif action == _g:
            ev = yield
            if code(ev) == _g:
                _moveCursor(self._qpart, 'gg', select=True)

            raise StopIteration(True)
        elif action == _r:
            ev = yield
            newChar = ev.text()
            if newChar:
                newChars = [newChar if char != '\n' else '\n' \
                                for char in self._qpart.selectedText
                            ]
                newText = ''.join(newChars)
                self._qpart.selectedText = newText
            raise StopIteration(True)
        elif ev.text():
            raise StopIteration(True)  # ignore unknown character
        else:
            raise StopIteration(False)  # but do not ignore not-a-character keys

        assert 0  # must StopIteration on if



    #
    # Simple commands
    #

    def cmdDelete(self, cmd):
        cursor = self._qpart.textCursor()
        if cursor.selectedText():
            self._vim.internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()

    def cmdInsertMode(self, cmd):
        self.switchMode(Insert)

    def cmdNormalMode(self, cmd):
        self.switchMode(Normal)

    def cmdAppendAfterChar(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.Right)
        self._qpart.setTextCursor(cursor)
        self.switchMode(Insert)

    def cmdReplaceSelectedLines(self, cmd):
        ((startLine, startCol), (endLine, endCol)) = self._qpart.selectedPosition

        self._vim.internalClipboard = self._qpart.lines[startLine:endLine + 1]

        lastLineLen = len(self._qpart.lines[endLine])
        self._qpart.selectedPosition = ((startLine, 0), (endLine, lastLineLen))
        self._qpart.selectedText = ''

        self.switchMode(Insert)

    def cmdResetSelection(self, cmd):
        self._qpart.cursorPosition = self._qpart.selectedPosition[0]

    def cmdInternalPaste(self, cmd):
        if not self._vim.internalClipboard:
            return

        if isinstance(self._vim.internalClipboard, basestring):
            self._qpart.textCursor().insertText(self._vim.internalClipboard)
        elif isinstance(self._vim.internalClipboard, list):
            currentLineIndex = self._qpart.cursorPosition[0]
            self._qpart.lines.insert(currentLineIndex + 1, '\n'.join(self._vim.internalClipboard))

    def cmdYank(self, cmd):
        self._qpart.copy()
        self._vim.internalClipboard = self._qpart.selectedText

    def cmdChange(self, cmd):
        cursor = self._qpart.textCursor()
        if cursor.selectedText():
            self._vim.internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()
        self.switchMode(Insert)


    _SIMPLE_COMMANDS = {
                            _A: cmdAppendAfterChar,
                            _c: cmdChange,
                            _d: cmdDelete,
                            _i: cmdInsertMode,
                            _x: cmdDelete,
                            _R: cmdReplaceSelectedLines,
                            _p: cmdInternalPaste,
                            _u: cmdResetSelection,
                            _y: cmdYank,
                            _Esc: cmdNormalMode,
                       }


class Normal(Mode):
    color = QColor('#33cc33')

    def __init__(self, *args):
        Mode.__init__(self, *args)
        self._reset()

    def _reset(self):
        self._processCharCoroutine = self._processChar()
        self._processCharCoroutine.next()  # run until the first yield
        self._typedText = ''

    def text(self):
        return self._typedText or 'normal'

    def keyPressEvent(self, ev):
        self._typedText += ev.text()
        try:
            self._processCharCoroutine.send(ev)
        except StopIteration as ex:
            retVal = ex.args[0]
            self._reset()
        else:
            retVal = True

        self._vim.updateIndication()

        return retVal

    def _processChar(self):
        ev = yield None

        # Get action count
        actionCount = 0

        if ev.key() != _0:
            char = ev.text()
            while char.isdigit():
                digit = int(char)
                actionCount = (actionCount * 10) + digit
                ev = yield
                char = ev.text()

        if actionCount == 0:
            actionCount = 1

        # Now get the action
        action = code(ev)
        if action == _x:
            """ Delete command is a special case.
            It accumulates deleted text in the internal clipboard. Give count as a command parameter
            """
            self.cmdDelete(actionCount)
            raise StopIteration(True)
        elif action in self._SIMPLE_COMMANDS:
            cmdFunc = self._SIMPLE_COMMANDS[action]

            if actionCount != 1:
                with self._qpart:
                    for _ in range(actionCount):
                        cmdFunc(self, action)
            else:
                cmdFunc(self, action)

            raise StopIteration(True)
        elif action in _MOTIONS:
            for _ in range(actionCount):
                _moveCursor(self._qpart, action, select=False)
            raise StopIteration(True)
        elif action == _g:
            ev = yield
            if code(ev) == _g:
                _moveCursor(self._qpart, 'gg')

            raise StopIteration(True)
        elif action in (_c, _d):
            moveCount = 0
            ev = yield

            if ev.key() != _0:  # 0 is a command, not a count
                char = ev.text()
                while char.isdigit():
                    digit = int(char)
                    moveCount = (moveCount * 10) + digit
                    ev = yield
                    char = ev.text()

            if moveCount == 0:
                moveCount = 1

            count = actionCount * moveCount

            # Get motion for a composite command
            motion = code(ev)
            if motion == _g:
                ev = yield
                if code(ev) == _g:
                    motion = 'gg'
                else:
                    raise StopIteration(True)

            # TODO verify if motion is valid

            cmdFunc = self._COMPOSITE_COMMANDS[action]
            cmdFunc(self, action, motion, count)

            raise StopIteration(True)
        elif ev.text() == 1:
            raise StopIteration(True)  # ignore unknown character
        else:
            raise StopIteration(False)  # but do not ignore not-a-character keys


        assert 0  # must StopIteration on if

    #
    # Simple commands
    #

    def cmdInsertMode(self, cmd):
        self.switchMode(Insert)

    def cmdReplaceMode(self, cmd):
        self.switchMode(Replace)
        self._qpart.setOverwriteMode(True)

    def cmdReplaceCharMode(self, cmd):
        self.switchMode(ReplaceChar)
        self._qpart.setOverwriteMode(True)

    def cmdAppendAfterLine(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        self._qpart.setTextCursor(cursor)
        self.switchMode(Insert)

    def cmdAppendAfterChar(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.Right)
        self._qpart.setTextCursor(cursor)
        self.switchMode(Insert)

    def cmdUndo(self, cmd):
        self._qpart.undo()

    def cmdInternalPaste(self, cmd):
        if not self._vim.internalClipboard:
            return

        if isinstance(self._vim.internalClipboard, basestring):
            self._qpart.textCursor().insertText(self._vim.internalClipboard)
        elif isinstance(self._vim.internalClipboard, list):
            currentLineIndex = self._qpart.cursorPosition[0]
            self._qpart.lines.insert(currentLineIndex + 1, '\n'.join(self._vim.internalClipboard))

    def cmdVisualMode(self, cmd):
        self.switchMode(Visual)

    #
    # Special cases
    #
    def cmdDelete(self, count):
        cursor = self._qpart.textCursor()
        for _ in xrange(count):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        if cursor.selectedText():
            self._vim.internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()


    _SIMPLE_COMMANDS = {_A: cmdAppendAfterLine,
                        _a: cmdAppendAfterChar,
                        _i: cmdInsertMode,
                        _r: cmdReplaceCharMode,
                        _R: cmdReplaceMode,
                        _v: cmdVisualMode,
                        _p: cmdInternalPaste,
                        _u: cmdUndo,
                       }

    #
    # Composite commands
    #

    def cmdCompositeDelete(self, cmd, motion, count):
        if motion == _j:  # down
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex
            if availableCount < 2:  # last line
                return

            effectiveCount = min(availableCount, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
        elif motion == _k:  # up
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == 0:  # first line
                return

            effectiveCount = min(lineIndex, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
            del self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
        elif motion == _d:  # delete whole line
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex

            effectiveCount = min(availableCount, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount]
        elif motion == _G:
            currentLineIndex = self._qpart.cursorPosition[0]
            self._vim.internalClipboard = self._qpart.lines[currentLineIndex:]
            del self._qpart.lines[currentLineIndex:]
        elif motion == 'gg':
            currentLineIndex = self._qpart.cursorPosition[0]
            self._vim.internalClipboard = self._qpart.lines[:currentLineIndex + 1]
            del self._qpart.lines[:currentLineIndex + 1]
        elif motion in (_h, _l, _w, _e, _Dollar, _0):
            for _ in xrange(count):
                _moveCursor(self._qpart, motion, select=True)

            selText = self._qpart.textCursor().selectedText()
            if selText:
                self._vim.internalClipboard = selText
                self._qpart.textCursor().removeSelectedText()

    def cmdCompositeChange(self, cmd, motion, count):
        # TODO deletion and next insertion should be undo-ble as 1 action
        self.cmdCompositeDelete(cmd, motion, count)
        self.switchMode(Insert)

    _COMPOSITE_COMMANDS = {_c: cmdCompositeChange,
                           _d: cmdCompositeDelete,
                          }
