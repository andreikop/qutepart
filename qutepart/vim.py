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
        self._mode = NORMAL
        self._pendingOperator = None
        self._pendingCount = 0
        self._internalClipboard = ''  # delete commands save text to this clipboard

    def isActive(self):
        return True

    def indication(self):
        color = MODE_COLORS[self._mode]
        text = ''

        if self._pendingCount:
            text += str(self._pendingCount)

        if self._pendingOperator:
            text += self._pendingOperator

        if not text:
            text = self._mode

        return color, text

    def _updateIndication(self):
        self.modeIndicationChanged.emit(*self.indication())

    def normalKeyPress(self, event):
        text = event.text()

        if not text:
            return

        simpleCommands = self._COMMANDS['simple']
        compositeCommands = self._COMMANDS['composite']

        def runFunc(cmdFunc, *args):
            if self._pendingCount:
                with self._qpart:
                    for _ in range(self._pendingCount):
                        cmdFunc(self, *args)
            else:
                cmdFunc(self, *args)

        if text.isdigit() and (text != '0' or self._pendingCount):  # 0 is a command, not a count
            digit = int(text)
            self._pendingCount = (self._pendingCount * 10)+ digit
            self._updateIndication()
            return True
        elif self._pendingOperator:
            cmdFunc = self._COMMANDS['composite'][self._pendingOperator]
            cmdFunc(self, self._pendingOperator, text, self._pendingCount or 1)
            self._pendingOperator = None
            self._pendingCount = 0
            self._updateIndication()
            return True
        elif text == 'x':
            """ Delete command is special case.
            It accumulates deleted text in the internal clipboard
            """
            self.cmdDelete(self._pendingCount or 1)
            self._pendingCount = 0
            self._updateIndication()
            return True
        elif text in simpleCommands:
            cmdFunc = simpleCommands[text]
            runFunc(cmdFunc, text)
            self._pendingCount = 0
            self._updateIndication()
            return True
        elif text in compositeCommands:
            self._pendingOperator = text
            self._updateIndication()
            return True
        else:
            return False

    def replaceCharKeyPress(self, event):
        if event.text():
            self._qpart.setOverwriteMode(False)
            line, col = self._qpart.cursorPosition
            if col > 0:
                self._qpart.cursorPosition = (line, col - 1)  # return the cursor back after replacement
            self._setMode(NORMAL)
            return False

    def insertKeyPress(self, event):
        if event.text() == '\x1b':  # ESC
            self._setMode(NORMAL)
            return True

    def keyPressEvent(self, event):
        """Check the event. Return True if processed and False otherwise
        """
        handlers = {NORMAL: self.normalKeyPress,
                    INSERT: self.insertKeyPress,
                    REPLACE_CHAR: self.replaceCharKeyPress}

        return handlers[self._mode](event)

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

    def _setMode(self, mode):
        self._mode = mode
        self._updateIndication()

    def cmdInsertMode(self, cmd): self._setMode(INSERT)

    def cmdReplaceCharMode(self, cmd):
        self._setMode(REPLACE_CHAR)
        self._qpart.setOverwriteMode(True)

    def cmdAppend(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        self._qpart.setTextCursor(cursor)
        self._setMode(INSERT)

    def cmdUndo(self, cmd):
        self._qpart.undo()

    def cmdInternalPaste(self, cmd):
        if not self._internalClipboard:
            return

        if isinstance(self._internalClipboard, basestring):
            self._qpart.textCursor().insertText(self._internalClipboard)
        elif isinstance(self._internalClipboard, list):
            currentLineIndex = self._qpart.cursorPosition[0]
            self._qpart.lines.insert(currentLineIndex + 1, '\n'.join(self._internalClipboard))

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

            self._internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount + 1]
        elif motion == 'k':  # up
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == 0:  # first line
                return

            effectiveCount = min(lineIndex, count)

            self._internalClipboard = self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
            del self._qpart.lines[lineIndex - effectiveCount:lineIndex + 1]
        elif motion == 'd':  # delete whole line
            lineIndex = self._qpart.cursorPosition[0]
            availableCount = len(self._qpart.lines) - lineIndex

            effectiveCount = min(availableCount, count)

            self._internalClipboard = self._qpart.lines[lineIndex:lineIndex + effectiveCount]
            del self._qpart.lines[lineIndex:lineIndex + effectiveCount]
        elif motion in 'hlwe$0':
            for _ in xrange(count):
                self._moveCursor(motion, select=True)

            selText = self._qpart.textCursor().selectedText()
            if selText:
                self._internalClipboard = selText
                self._qpart.textCursor().removeSelectedText()

    def cmdCompositeChange(self, cmd, motion, count):
        # TODO deletion and next insertion should be undo-ble as 1 action
        self.cmdCompositeDelete(cmd, motion, count)
        self._setMode(INSERT)

    #
    # Special cases
    #
    def cmdDelete(self, count):
        cursor = self._qpart.textCursor()
        for _ in xrange(count):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        if cursor.selectedText():
            self._internalClipboard = cursor.selectedText()
            cursor.removeSelectedText()


    _COMMANDS = {'simple': {'i': cmdInsertMode,
                            'r': cmdReplaceCharMode,
                            'j': cmdMove,
                            'k': cmdMove,
                            'h': cmdMove,
                            'l': cmdMove,
                            'w': cmdMove,
                            'e': cmdMove,
                            '$': cmdMove,
                            '0': cmdMove,
                            'A': cmdAppend,
                            'u': cmdUndo,
                            'p': cmdInternalPaste,
                           },
                 'composite': {'c': cmdCompositeChange,
                               'd': cmdCompositeDelete,
                              }
                }
