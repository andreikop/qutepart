from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QColor, QTextCursor


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

    def isActive(self):
        return True

    def indication(self):
        return self._mode.color, self._mode.text()

    def updateIndication(self):
        self.modeIndicationChanged.emit(*self.indication())


    def keyPressEvent(self, event):
        """Check the event. Return True if processed and False otherwise
        """
        return self._mode.keyPressEvent(event.text())


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

    def keyPressEvent(self, text):
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

    def keyPressEvent(self, text):
        if text == '\x1b':  # ESC
            self.switchMode(Normal)
            return True

        return False


class ReplaceChar(Mode):
    color = QColor('#ff3300')

    def text(self):
        return 'replace char'

    def keyPressEvent(self, text):
        if text:
            self._qpart.setOverwriteMode(False)
            line, col = self._qpart.cursorPosition
            if col > 0:
                self._qpart.cursorPosition = (line, col - 1)  # return the cursor back after replacement
            self.switchMode(Normal)


class NormalBase(Mode):
    """Base class for normal modes
    """
    color = QColor('#33cc33')

    def _moveCursor(self, motion, select=False):
        cursor = self._qpart.textCursor()

        moveMode = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor

        moveOperation = {'j': QTextCursor.Down,
                         'k': QTextCursor.Up,
                         'h': QTextCursor.Left,
                         'l': QTextCursor.Right,
                         'w': QTextCursor.WordRight,
                         '$': QTextCursor.EndOfLine,
                         '0': QTextCursor.StartOfLine,
                         'gg': QTextCursor.Start,
                         'G': QTextCursor.End
                        }

        if motion in moveOperation:
            cursor.movePosition(moveOperation[motion], moveMode)
        elif motion == 'e':
            oldPos = cursor.position()
            cursor.movePosition(QTextCursor.EndOfWord, moveMode)
            if cursor.position() == oldPos:
                cursor.movePosition(QTextCursor.Right, moveMode)
                cursor.movePosition(QTextCursor.EndOfWord, moveMode)

        self._qpart.setTextCursor(cursor)


class Normal(NormalBase):
    """Normal mode.
    Command processing stage 1.
    Waiting for command count
    """
    def __init__(self, *args):
        NormalBase.__init__(self, *args)
        self._actionCount = 0

    def text(self):
        if self._actionCount:
            return str(self._actionCount)
        else:
            return 'normal'

    def keyPressEvent(self, text):
        if not text:
            return

        if text.isdigit() and (text != '0' or self._actionCount):
            digit = int(text)
            self._actionCount = (self._actionCount * 10) + digit
            self._vim.updateIndication()
            return True
        else:
            count = self._actionCount or 1
            return self.switchModeAndProcess(text, NormalGetAction, count)


class NormalGetAction(NormalBase):
    """Normal mode command processing stage 2.
    Waiting for action.
    Process simple actions. Switch to next mode if got composite action.
    """

    def __init__(self, vim, qpart, actionCount):
        NormalBase.__init__(self, vim, qpart)
        self._actionCount = actionCount

    def text(self):
        if self._actionCount != 1:
            return str(self._actionCount)
        else:
            return 'normal'

    def keyPressEvent(self, text):
        if text == 'x':
            """ Delete command is special case.
            It accumulates deleted text in the internal clipboard
            """
            self.cmdDelete(self._actionCount)
            self.switchMode(Normal)
            return True
        elif text in self._SIMPLE_COMMANDS:
            self.switchMode(Normal)  # switch to normal BEFORE executing command. Command may switch mode once more
            cmdFunc = self._SIMPLE_COMMANDS[text]

            if self._actionCount != 1:
                with self._qpart:
                    for _ in range(self._actionCount):
                        cmdFunc(self, text)
            else:
                cmdFunc(self, text)

            return True
        elif text in 'cdg':
            self.switchMode(NormalGetCompositeActionMoveCount, self._actionCount, text)
            return True
        else:
            self.switchMode(Normal)
            return False

    #
    # Simple commands
    #

    def cmdMove(self, cmd):
        self._moveCursor(cmd, select=False)

    def cmdInsertMode(self, cmd):
        self.switchMode(Insert)

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


    _SIMPLE_COMMANDS = {'i': cmdInsertMode,
                        'r': cmdReplaceCharMode,
                        'j': cmdMove,
                        'k': cmdMove,
                        'h': cmdMove,
                        'l': cmdMove,
                        'w': cmdMove,
                        'e': cmdMove,
                        '$': cmdMove,
                        '0': cmdMove,
                        'G': cmdMove,
                        'A': cmdAppendAfterLine,
                        'a': cmdAppendAfterChar,
                        'u': cmdUndo,
                        'p': cmdInternalPaste,
                       }


class NormalGetCompositeActionMoveCount(NormalBase):
    """Normal mode.
    Got action count and composite action.
    Get move count
    """
    def __init__(self, vim, qpart, actionCount, action):
        NormalBase.__init__(self, vim, qpart)
        self._actionCount = actionCount
        self._action = action
        self._moveCount = 0
        self._pendingMotion = ''

    def text(self):
        count = '' if self._actionCount == 1 else str(self._actionCount)
        return count + self._action

    def keyPressEvent(self, text):
        if text.isdigit() and (text != '0' or self._moveCount):  # 0 is a command, not a count
            digit = int(text)
            self._moveCount = (self._moveCount * 10)+ digit
            self._vim.updateIndication()
            return True
        else:
            count = (self._moveCount or 1) * self._actionCount
            return self.switchModeAndProcess(text, NormalGetCompositeActionMove, count, self._action)



class NormalGetCompositeActionMove(NormalBase):
    """Normal mode.
    Got action count and action. Get move count
    """
    def __init__(self, vim, qpart, count, action):
        NormalBase.__init__(self, vim, qpart)
        self._count = count
        self._action = action
        self._pendingMotion = ''

    def text(self):
        count = '' if self._count == 1 else str(self._count)
        return count + self._action

    def keyPressEvent(self, text):
        if text == 'g' and self._action != 'g':
            if self._pendingMotion:
                motion = self._pendingMotion + text
                self._pendingMotion = ''
            else:
                self._pendingMotion = text
                return True
        else:
            motion = text

        self.switchMode(Normal)  # switch to normal BEFORE executing command. Command may switch mode once more
        cmdFunc = self._COMPOSITE_COMMANDS[self._action]
        cmdFunc(self, self._action, motion, self._count)
        return True

    #
    # Composite commands
    #

    def cmdCompositeDelete(self, cmd, motion, count):
        if motion == 'j':  # down
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex
            if availableCount < 2:  # last line
                return

            effectiveCount = min(availableCount, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
        elif motion == 'k':  # up
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == 0:  # first line
                return

            effectiveCount = min(lineIndex, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
            del self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
        elif motion == 'd':  # delete whole line
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex

            effectiveCount = min(availableCount, count)

            self._vim.internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount]
        elif motion == 'G':
            currentLineIndex = self._qpart.cursorPosition[0]
            self._vim.internalClipboard = self._qpart.lines[currentLineIndex:]
            del self._qpart.lines[currentLineIndex:]
        elif motion == 'gg':
            currentLineIndex = self._qpart.cursorPosition[0]
            self._vim.internalClipboard = self._qpart.lines[:currentLineIndex + 1]
            del self._qpart.lines[:currentLineIndex + 1]
        elif motion in 'hlwe$0':
            for _ in xrange(count):
                self._moveCursor(motion, select=True)

            selText = self._qpart.textCursor().selectedText()
            if selText:
                self._vim.internalClipboard = selText
                self._qpart.textCursor().removeSelectedText()

    def cmdCompositeChange(self, cmd, motion, count):
        # TODO deletion and next insertion should be undo-ble as 1 action
        self.cmdCompositeDelete(cmd, motion, count)
        self.switchMode(Insert)

    def cmdCompositeGMove(self, cmd, motion, count):
        if motion == 'g':
            self._moveCursor('gg')

    _COMPOSITE_COMMANDS = {'c': cmdCompositeChange,
                           'd': cmdCompositeDelete,
                           'g': cmdCompositeGMove,
                          }
