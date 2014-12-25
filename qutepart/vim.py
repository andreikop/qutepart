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
        self.updateIndication()

    def indication(self):
        return self._mode.color, self._mode.text()

    def updateIndication(self):
        self.modeIndicationChanged.emit(*self.indication())


    def keyPressEvent(self, event):
        """Check the event. Return True if processed and False otherwise
        """
        text = event.text()

        if not text:
            return False

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


class Normal(Mode):
    color = QColor('#33cc33')

    def __init__(self, *args):
        Mode.__init__(self, *args)
        self._reset()

    def _reset(self):
        self._processCharCoroutine = self._processChar()
        self._processCharCoroutine.next()  # run until first yield
        self._typedText = ''

    def text(self):
        return self._typedText or 'normal'

    def keyPressEvent(self, char):
        self._typedText += char
        try:
            self._processCharCoroutine.send(char)
        except StopIteration:
            self._reset()

        self._vim.updateIndication()

        return True

    def _processChar(self):
        char = yield None

        # Get action count
        actionCount = 0

        while char.isdigit() and (actionCount or char != '0'):
            digit = int(char)
            actionCount = (actionCount * 10) + digit
            char = yield

        if actionCount == 0:
            actionCount = 1

        # Now get the action
        action = char
        if action == 'x':
            """ Delete command is a special case.
            It accumulates deleted text in the internal clipboard. Give count as a command parameter
            """
            self.cmdDelete(actionCount)
            return
        elif action in self._SIMPLE_COMMANDS:
            cmdFunc = self._SIMPLE_COMMANDS[action]

            if actionCount != 1:
                with self._qpart:
                    for _ in range(actionCount):
                        cmdFunc(self, action)
            else:
                cmdFunc(self, action)

            return
        elif action == 'g':
            char = yield
            if char == 'g':
                self._moveCursor('gg')

            return
        elif action in 'cd':
            moveCount = 0
            char = yield
            while char.isdigit() and (char != '0' or moveCount):  # 0 is a command, not a count
                digit = int(char)
                moveCount = (moveCount * 10) + digit
                char = yield

            if moveCount == 0:
                moveCount = 1

            count = actionCount * moveCount

            # Get motion for a composite command
            motion = char
            if motion == 'g':
                char = yield
                if char == 'g':
                    motion += 'g'
                else:
                    return

            # TODO verify if motion is valid

            cmdFunc = self._COMPOSITE_COMMANDS[action]
            cmdFunc(self, action, motion, count)

            return

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

    _COMPOSITE_COMMANDS = {'c': cmdCompositeChange,
                           'd': cmdCompositeDelete,
                          }
