import sys

from PyQt4.QtCore import Qt, pyqtSignal, QObject
from PyQt4.QtGui import QColor, QTextCursor


""" This magic code sets variables like _a and _A in the global scope
"""
thismodule = sys.modules[__name__]
for charCode in range(ord('a'), ord('z') + 1):
    shortName = chr(charCode)
    longName = 'Key_' + shortName.upper()
    qtCode = getattr(Qt, longName)
    setattr(thismodule, '_' + shortName, qtCode)
    setattr(thismodule, '_' + shortName.upper(), Qt.ShiftModifier + qtCode)

_0 = Qt.Key_0
_Dollar = Qt.ShiftModifier + Qt.Key_Dollar
_Percent = Qt.ShiftModifier + Qt.Key_Percent
_Caret = Qt.ShiftModifier + Qt.Key_AsciiCircum
_Esc = Qt.Key_Escape
_Insert = Qt.Key_Insert
_Down = Qt.Key_Down
_Up = Qt.Key_Up
_Left = Qt.Key_Left
_Right = Qt.Key_Right
_Space = Qt.Key_Space
_BackSpace = Qt.Key_Backspace
_Equal = Qt.Key_Equal
_Less = Qt.ShiftModifier + Qt.Key_Less
_Greater = Qt.ShiftModifier + Qt.Key_Greater
_Home = Qt.Key_Home
_End = Qt.Key_End


def code(ev):
    modifiers = ev.modifiers()
    modifiers &= ~Qt.KeypadModifier  # ignore keypad modifier to handle both main and numpad numbers
    return int(modifiers) + ev.key()

def isChar(ev):
    """ Check if an event may be a typed character
    """
    text = ev.text()
    if len(text) != 1:
        return False

    if ev.modifiers() not in (Qt.ShiftModifier, Qt.KeypadModifier, Qt.NoModifier):
        return False

    asciiCode = ord(text)
    if asciiCode <= 31 or asciiCode == 0x7f:  # control characters
        return False

    if text == ' ' and ev.modifiers() == Qt.ShiftModifier:
        return False  # Shift+Space is a shortcut, not a text

    return True


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

    internalClipboard = ''  # delete commands save text to this clipboard

    def __init__(self, qpart):
        QObject.__init__(self)
        self._qpart = qpart
        self._mode = Normal(self, qpart)

        self._qpart.selectionChanged.connect(self._onSelectionChanged)

        self._processingKeyPress = False

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

        self._processingKeyPress = True
        try:
            ret = self._mode.keyPressEvent(ev)
        finally:
            self._processingKeyPress = False
        return ret

    def inInsertMode(self):
        return isinstance(self._mode, Insert)

    def setMode(self, mode):
        self._mode = mode
        self.updateIndication()

    def _onSelectionChanged(self):
        if not self._processingKeyPress:
            if self._qpart.selectedText:
                if not isinstance(self._mode, (Visual, VisualLines)):
                    self.setMode(Visual(self, self._qpart))
            else:
                self.setMode(Normal(self, self._qpart))



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
        if isChar(ev):  # a char
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


class BaseCommandMode(Mode):
    """ Base class for Normal and Visual modes
    """
    def __init__(self, *args):
        Mode.__init__(self, *args)
        self._reset()

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

    def text(self):
        return self._typedText or self.name

    def _reset(self):
        self._processCharCoroutine = self._processChar()
        self._processCharCoroutine.next()  # run until the first yield
        self._typedText = ''

    _MOTIONS = (_0, _Home,
                _Dollar, _End,
                _Percent, _Caret,
                _b,
                _e,
                _G,
                _j, _Down,
                _l, _Right, _Space,
                _k, _Up,
                _h, _Left, _BackSpace,
                _w,
                'gg',
                _f, _F, _t, _T,
                )

    def _moveCursor(self, motion, count, searchChar=None, select=False):
        """ Move cursor.
        Used by Normal and Visual mode
        """
        cursor = self._qpart.textCursor()

        effectiveCount = count or 1

        moveMode = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor

        moveOperation = {_b: QTextCursor.WordLeft,
                         _j: QTextCursor.Down,
                         _Down: QTextCursor.Down,
                         _k: QTextCursor.Up,
                         _Up: QTextCursor.Up,
                         _h: QTextCursor.Left,
                         _Left: QTextCursor.Left,
                         _BackSpace: QTextCursor.Left,
                         _l: QTextCursor.Right,
                         _Right: QTextCursor.Right,
                         _Space: QTextCursor.Right,
                         _w: QTextCursor.WordRight,
                         _Dollar: QTextCursor.EndOfLine,
                         _End: QTextCursor.EndOfLine,
                         _0: QTextCursor.StartOfLine,
                         _Home: QTextCursor.StartOfLine,
                         'gg': QTextCursor.Start,
                         _G: QTextCursor.End
                        }

        def moveToFirstNonSpace():
            text = cursor.block().text()
            spaceLen = len(text) - len(text.lstrip())
            cursor.setPosition(cursor.block().position() + spaceLen, moveMode)

        if motion == _G:
            if count == 0:  # default - go to the end
                cursor.movePosition(QTextCursor.End, moveMode)
            else:  # if count is set - move to line
                block = self._qpart.document().findBlockByNumber(count - 1)
                if not block.isValid():
                    return
                cursor.setPosition(block.position(), moveMode)
            moveToFirstNonSpace()
        elif motion in moveOperation:
            for _ in range(effectiveCount):
                cursor.movePosition(moveOperation[motion], moveMode)
        elif motion == _e:
            for _ in range(effectiveCount):
                # skip spaces
                text = cursor.block().text()
                pos = cursor.positionInBlock()
                for char in text[pos:]:
                    if char.isspace():
                        cursor.movePosition(QTextCursor.NextCharacter, moveMode)
                    else:
                        break

                if cursor.positionInBlock() == len(text):  # at the end of line
                    cursor.movePosition(QTextCursor.NextCharacter, moveMode)  # move to the next line

                # now move to the end of word
                cursor.movePosition(QTextCursor.EndOfWord, moveMode)
        elif motion == _Percent:
            # Percent move is done only once
            if self._qpart._bracketHighlighter.currentMatchedBrackets is not None:
                ((startBlock, startCol), (endBlock, endCol)) = self._qpart._bracketHighlighter.currentMatchedBrackets
                startPos = startBlock.position() + startCol
                endPos = endBlock.position() + endCol
                if select and \
                   (endPos > startPos):
                    endPos += 1  # to select the bracket, not only chars before it
                cursor.setPosition(endPos, moveMode)
        elif motion == _Caret:
            # Caret move is done only once
            moveToFirstNonSpace()
        elif motion in (_f, _F, _t, _T):
            if motion in (_f, _t):
                iterator = self._iterateDocumentCharsForward(cursor.block(), cursor.columnNumber())
                stepBack = QTextCursor.Left
            else:
                iterator = self._iterateDocumentCharsBackward(cursor.block(), cursor.columnNumber())
                stepBack = QTextCursor.Right

            for block, columnIndex, char in iterator:
                if char == searchChar:
                    cursor.setPosition(block.position() + columnIndex, moveMode)
                    if motion in (_t, _T):
                        cursor.movePosition(stepBack, moveMode)
                    break
        else:
            assert 0, 'Not expected motion ' + str(motion)

        self._qpart.setTextCursor(cursor)

    def _iterateDocumentCharsForward(self, block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        Raise _TimeoutException if time is over
        """
        # Chars in the start line
        for columnIndex, char in list(enumerate(block.text()))[startColumnIndex:]:
            yield block, columnIndex, char
        block = block.next()

        # Next lines
        while block.isValid():
            for columnIndex, char in enumerate(block.text()):
                yield block, columnIndex, char

            block = block.next()

    def _iterateDocumentCharsBackward(self, block, startColumnIndex):
        """Traverse document forward. Yield (block, columnIndex, char)
        Raise _TimeoutException if time is over
        """
        # Chars in the start line
        for columnIndex, char in reversed(list(enumerate(block.text()[:startColumnIndex]))):
            yield block, columnIndex, char
        block = block.previous()

        # Next lines
        while block.isValid():
            for columnIndex, char in reversed(list(enumerate(block.text()))):
                yield block, columnIndex, char

            block = block.previous()

    def _resetSelection(self, moveToAncor=False):
        """ Reset selection.
        If moveToStart is True - move cursor to the ancor position
        """
        index = 0 if moveToAncor else 1
        self._qpart.cursorPosition = self._qpart.selectedPosition[index]




class BaseVisual(BaseCommandMode):
    color = QColor('#6699ff')
    _selectLines = NotImplementedError()

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
            for _ in range(count):
                cmdFunc(self, action)
            if action not in (_v, _V):  # if not switched to another visual mode
                self._resetSelection()
            raise StopIteration(True)
        elif action == _g:
            ev = yield
            if code(ev) == _g:
                self._moveCursor('gg', 1, select=True)
                if self._selectLines:
                    self._expandSelection()
            raise StopIteration(True)
        elif action in (_f, _F, _t, _T):
            ev = yield
            if not isChar(ev):
                raise StopIteration(True)

            searchChar = ev.text()
            self._moveCursor(action, count, searchChar=searchChar, select=True)
            raise StopIteration(True)
        elif action in self._MOTIONS:
            self._moveCursor(action, count, select=True)
            if self._selectLines:
                self._expandSelection()
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
        elif isChar(ev):
            raise StopIteration(True)  # ignore unknown character
        else:
            raise StopIteration(False)  # but do not ignore not-a-character keys

        assert 0  # must StopIteration on if

    def _expandSelection(self):
        cursor = self._qpart.textCursor()
        anchor = cursor.anchor()
        pos = cursor.position()


        if pos >= anchor:
            anchorSide = QTextCursor.StartOfLine
            cursorSide = QTextCursor.EndOfLine
        else:
            anchorSide = QTextCursor.EndOfLine
            cursorSide = QTextCursor.StartOfLine


        cursor.setPosition(anchor)
        cursor.movePosition(anchorSide)
        cursor.setPosition(pos, QTextCursor.KeepAnchor)
        cursor.movePosition(cursorSide, QTextCursor.KeepAnchor)

        self._qpart.setTextCursor(cursor)

    def _selectedLinesRange(self):
        """ Selected lines range for line manipulation methods
        """
        (startLine, startCol), (endLine, endCol) = self._qpart.selectedPosition
        start = min(startLine, endLine)
        end = max(startLine, endLine)
        return start, end

    #
    # Simple commands
    #

    def cmdDelete(self, cmd):
        cursor = self._qpart.textCursor()
        if cursor.selectedText():
            if self._selectLines:
                start, end  = self._selectedLinesRange()
                Vim.internalClipboard = self._qpart.lines[start:end + 1]
                del self._qpart.lines[start:end + 1]
            else:
                Vim.internalClipboard = cursor.selectedText()
                cursor.removeSelectedText()

    def cmdDeleteLines(self, cmd):
        cursor = self._qpart.textCursor()
        start, end  = self._selectedLinesRange()
        Vim.internalClipboard = self._qpart.lines[start:end + 1]
        del self._qpart.lines[start:end + 1]

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
        start, end = self._selectedLinesRange()
        Vim.internalClipboard = self._qpart.lines[start:end + 1]

        lastLineLen = len(self._qpart.lines[end])
        self._qpart.selectedPosition = ((start, 0), (end, lastLineLen))
        self._qpart.selectedText = ''

        self.switchMode(Insert)

    def cmdResetSelection(self, cmd):
        self._qpart.cursorPosition = self._qpart.selectedPosition[0]

    def cmdInternalPaste(self, cmd):
        if not Vim.internalClipboard:
            return

        with self._qpart:
            cursor = self._qpart.textCursor()

            if self._selectLines:
                start, end = self._selectedLinesRange()
                del self._qpart.lines[start:end + 1]
            else:
                cursor.removeSelectedText()

            if isinstance(Vim.internalClipboard, basestring):
                self._qpart.textCursor().insertText(Vim.internalClipboard)
            elif isinstance(Vim.internalClipboard, list):
                currentLineIndex = self._qpart.cursorPosition[0]
                text = '\n'.join(Vim.internalClipboard)
                index = currentLineIndex if self._selectLines else currentLineIndex + 1
                self._qpart.lines.insert(index, text)

    def cmdVisualMode(self, cmd):
        if not self._selectLines:
            return  # already in visual mode
        self.switchMode(Visual)

    def cmdVisualLinesMode(self, cmd):
        if self._selectLines:
            return  # already in visual lines mode

        self.switchMode(VisualLines)

    def cmdYank(self, cmd):
        if self._selectLines:
            start, end = self._selectedLinesRange()
            Vim.internalClipboard = self._qpart.lines[start:end + 1]
        else:
            Vim.internalClipboard = self._qpart.selectedText

        self._qpart.copy()

    def cmdChange(self, cmd):
        cursor = self._qpart.textCursor()
        if cursor.selectedText():
            if self._selectLines:
                Vim.internalClipboard = cursor.selectedText().splitlines()
            else:
                Vim.internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()
        self.switchMode(Insert)

    def cmdUnIndent(self, cmd):
        self._qpart._indenter.onChangeSelectedBlocksIndent(increase=False, withSpace=False)

    def cmdIndent(self, cmd):
        self._qpart._indenter.onChangeSelectedBlocksIndent(increase=True, withSpace=False)

    def cmdAutoIndent(self, cmd):
        self._qpart._indenter.onAutoIndentTriggered()

    _SIMPLE_COMMANDS = {
                            _A: cmdAppendAfterChar,
                            _c: cmdChange,
                            _C: cmdReplaceSelectedLines,
                            _d: cmdDelete,
                            _D: cmdDeleteLines,
                            _i: cmdInsertMode,
                            _R: cmdReplaceSelectedLines,
                            _p: cmdInternalPaste,
                            _u: cmdResetSelection,
                            _x: cmdDelete,
                            _v: cmdVisualMode,
                            _V: cmdVisualLinesMode,
                            _X: cmdDeleteLines,
                            _y: cmdYank,
                            _Esc: cmdNormalMode,
                            _Less: cmdUnIndent,
                            _Greater: cmdIndent,
                            _Equal: cmdAutoIndent,
                       }


class Visual(BaseVisual):
    name = 'visual'

    _selectLines = False


class VisualLines(BaseVisual):
    name = 'visual lines'

    _selectLines = True

    def __init__(self, *args):
        BaseVisual.__init__(self, *args)
        self._expandSelection()


class Normal(BaseCommandMode):
    color = QColor('#33cc33')
    name = 'normal'

    def _processChar(self):
        ev = yield None
        # Get action count
        typedCount = 0

        if ev.key() != _0:
            char = ev.text()
            while char.isdigit():
                digit = int(char)
                typedCount = (typedCount * 10) + digit
                ev = yield
                char = ev.text()

        effectiveCount = typedCount or 1

        # Now get the action
        action = code(ev)


        if action in (_x, _X):
            """ Delete command is a special case.
            It accumulates deleted text in the internal clipboard. Give count as a command parameter
            """
            self.cmdDelete(effectiveCount, back=(action == _X))
            raise StopIteration(True)
        elif action in (_C, _D):
            self.cmdDeleteUntilEndOfLine(effectiveCount, action==_C)
            raise StopIteration(True)
        elif action in self._SIMPLE_COMMANDS:
            cmdFunc = self._SIMPLE_COMMANDS[action]

            if effectiveCount != 1:
                with self._qpart:
                    for _ in range(effectiveCount):
                        cmdFunc(self, action)
            else:
                cmdFunc(self, action)

            raise StopIteration(True)
        elif action == _g:
            ev = yield
            if code(ev) == _g:
                self._moveCursor('gg', 1)

            raise StopIteration(True)
        elif action in (_f, _F, _t, _T):
            ev = yield
            if not isChar(ev):
                raise StopIteration(True)

            searchChar = ev.text()
            self._moveCursor(action, effectiveCount, searchChar=searchChar, select=False)
            raise StopIteration(True)
        elif action in self._MOTIONS:
            self._moveCursor(action, typedCount, select=False)
            raise StopIteration(True)
        elif action in self._COMPOSITE_COMMANDS:
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

            count = effectiveCount * moveCount

            # Get motion for a composite command
            motion = code(ev)
            if motion == _g:
                ev = yield
                if code(ev) == _g:
                    motion = 'gg'
                else:
                    raise StopIteration(True)

            if (action != _z and motion in self._MOTIONS) or \
               (action, motion) in ((_d, _d),
                                    (_y, _y),
                                    (_Less, _Less),
                                    (_Greater, _Greater),
                                    (_Equal, _Equal),
                                    (_z, _z)):
                cmdFunc = self._COMPOSITE_COMMANDS[action]
                cmdFunc(self, action, motion, count)

            raise StopIteration(True)
        elif isChar(ev):
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

    def cmdRedo(self, cmd):
        self._qpart.redo()

    def cmdNewLineBelow(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        self._qpart.setTextCursor(cursor)
        self._qpart._insertNewBlock()
        self.switchMode(Insert)

    def cmdNewLineAbove(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        self._qpart.setTextCursor(cursor)
        self._qpart._insertNewBlock()
        cursor.movePosition(QTextCursor.Up)
        self._qpart.setTextCursor(cursor)
        self._qpart._indenter.autoIndentBlock(cursor.block())
        self.switchMode(Insert)

    def cmdInternalPaste(self, cmd):
        if not Vim.internalClipboard:
            return

        if isinstance(Vim.internalClipboard, basestring):
            self._qpart.textCursor().insertText(Vim.internalClipboard)
        elif isinstance(Vim.internalClipboard, list):
            currentLineIndex = self._qpart.cursorPosition[0]
            self._qpart.lines.insert(currentLineIndex + 1, '\n'.join(Vim.internalClipboard))

    def cmdVisualMode(self, cmd):
        self.switchMode(Visual)

    def cmdVisualLinesMode(self, cmd):
        self.switchMode(VisualLines)

    #
    # Special cases
    #
    def cmdDelete(self, count, back):
        """ x
        """
        cursor = self._qpart.textCursor()
        direction = QTextCursor.Left if back else QTextCursor.Right
        for _ in range(count):
            cursor.movePosition(direction, QTextCursor.KeepAnchor)

        if cursor.selectedText():
            Vim.internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()

    def cmdDeleteUntilEndOfLine(self, count, change):
        """ C and D
        """
        cursor = self._qpart.textCursor()
        for _ in range(count - 1):
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        Vim.internalClipboard = cursor.selectedText()
        cursor.removeSelectedText()
        if change:
            self.switchMode(Insert)


    _SIMPLE_COMMANDS = {_A: cmdAppendAfterLine,
                        _a: cmdAppendAfterChar,
                        _i: cmdInsertMode,
                        _r: cmdReplaceCharMode,
                        _R: cmdReplaceMode,
                        _v: cmdVisualMode,
                        _V: cmdVisualLinesMode,
                        _o: cmdNewLineBelow,
                        _O: cmdNewLineAbove,
                        _p: cmdInternalPaste,
                        _u: cmdUndo,
                        _U: cmdRedo,
                        # C, D, x, X are implemented as special cases
                       }

    #
    # Composite commands
    #

    def cmdCompositeDelete(self, cmd, motion, count):
        if motion in (_j, _Down):
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex
            if availableCount < 2:  # last line
                return

            effectiveCount = min(availableCount, count)

            Vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
        elif motion in (_k, _Up):
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == 0:  # first line
                return

            effectiveCount = min(lineIndex, count)

            Vim.internalClipboard = self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
            del self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
        elif motion == _d:  # delete whole line
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex

            effectiveCount = min(availableCount, count)

            Vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount]
        elif motion == _G:
            currentLineIndex = self._qpart.cursorPosition[0]
            Vim.internalClipboard = self._qpart.lines[currentLineIndex:]
            del self._qpart.lines[currentLineIndex:]
        elif motion == 'gg':
            currentLineIndex = self._qpart.cursorPosition[0]
            Vim.internalClipboard = self._qpart.lines[:currentLineIndex + 1]
            del self._qpart.lines[:currentLineIndex + 1]
        else:
            self._moveCursor(motion, count, select=True)

            selText = self._qpart.textCursor().selectedText()
            if selText:
                Vim.internalClipboard = selText
                self._qpart.textCursor().removeSelectedText()

    def cmdCompositeChange(self, cmd, motion, count):
        # TODO deletion and next insertion should be undo-ble as 1 action
        self.cmdCompositeDelete(cmd, motion, count)
        self.switchMode(Insert)

    def cmdCompositeYank(self, cmd, motion, count):
        oldCursor = self._qpart.textCursor()
        if motion == _y:
            cursor = self._qpart.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine)
            for _ in range(count - 1):
                cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            self._qpart.setTextCursor(cursor)
            Vim.internalClipboard = [self._qpart.selectedText]
        else:
            self._moveCursor(motion, count, select=True)
            Vim.internalClipboard = self._qpart.selectedText

        self._qpart.copy()
        self._qpart.setTextCursor(oldCursor)

    def cmdCompositeUnIndent(self, cmd, motion, count):
        if motion == _Less:
            pass  # current line is already selected
        else:
            self._moveCursor(motion, count, select=True)

        self._qpart._indenter.onChangeSelectedBlocksIndent(increase=False, withSpace=False)
        self._resetSelection(moveToAncor=True)

    def cmdCompositeIndent(self, cmd, motion, count):
        if motion == _Greater:
            pass  # current line is already selected
        else:
            self._moveCursor(motion, count, select=True)

        self._qpart._indenter.onChangeSelectedBlocksIndent(increase=True, withSpace=False)
        self._resetSelection(moveToAncor=True)

    def cmdCompositeAutoIndent(self, cmd, motion, count):
        if motion == _Equal:
            pass  # current line is already selected
        else:
            self._moveCursor(motion, count, select=True)

        self._qpart._indenter.onAutoIndentTriggered()
        self._resetSelection(moveToAncor=True)

    def cmdCompositeScrollView(self, cmd, motion, count):
        if motion == _z:
            self._qpart.centerCursor()

    _COMPOSITE_COMMANDS = {_c: cmdCompositeChange,
                           _d: cmdCompositeDelete,
                           _y: cmdCompositeYank,
                           _Less: cmdCompositeUnIndent,
                           _Greater: cmdCompositeIndent,
                           _Equal: cmdCompositeAutoIndent,
                           _z: cmdCompositeScrollView,
                          }
