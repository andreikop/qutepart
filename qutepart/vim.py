from PyQt4.QtCore import pyqtSignal, QObject, Qt
from PyQt4.QtGui import QColor, QTextCursor


NORMAL = 'normal'
INSERT = 'insert'

MODE_COLORS = {NORMAL: QColor('#33cc33'),
               INSERT: QColor('#ff9900')}

class Vim(QObject):
    """Vim mode implementation.
    Listens events and does actions
    """
    modeIndicationChanged = pyqtSignal(QColor, unicode)

    def __init__(self, qpart):
        QObject.__init__(self)
        self._qpart = qpart
        self._mode = NORMAL
        self._pendingCmd = None

    def isActive(self):
        return True

    def indication(self):
        return MODE_COLORS[self._mode], self._mode

    def keyPressEvent(self, event):
        """Check the event. Return True if processed and False otherwise
        """
        if not event.text():
            return

        simpleCommands = self._COMMANDS[self._mode]['simple']
        compositeCommands = self._COMMANDS[self._mode]['composite']

        if self._pendingCmd:
            cmdFunc = self._COMMANDS[self._mode]['composite'][self._pendingCmd]
            cmdFunc(self, self._pendingCmd, event.text())
            self._pendingCmd = None
            self.modeIndicationChanged.emit(MODE_COLORS[self._mode], self._mode)
            return True
        elif event.text() in simpleCommands:
            cmdFunc = simpleCommands[event.text()]
            cmdFunc(self, event.text())
            return True
        elif event.text() in compositeCommands:
            self._pendingCmd = event.text()
            self.modeIndicationChanged.emit(MODE_COLORS[self._mode], self._pendingCmd)
            return True
        else:
            return False

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
        self.modeIndicationChanged.emit(MODE_COLORS[mode], mode)

    def cmdInsertMode(self, cmd): self._setMode(INSERT)
    def cmdNormalMode(self, cmd): self._setMode(NORMAL)

    def cmdDelete(self, cmd):
        self._qpart.textCursor().deleteChar()

    def cmdAppend(self, cmd):
        cursor = self._qpart.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        self._qpart.setTextCursor(cursor)
        self._setMode(INSERT)

    #
    # Composite commands
    #

    def cmdCompositeDelete(self, cmd, motion):
        if motion == 'j':  # down
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == len(self._qpart.lines) - 1:  # last line
                return

            del self._qpart.lines[lineIndex:lineIndex + 2]

        elif motion == 'k':  # up
            lineIndex = self._qpart.cursorPosition[0]
            if lineIndex == 0:  # first line
                return

            del self._qpart.lines[lineIndex - 1:lineIndex + 1]
        elif motion in 'hlwe$0':
            self._moveCursor(motion, select=True)
            self._qpart.textCursor().removeSelectedText()



    _COMMANDS = {NORMAL: {'simple': {'i': cmdInsertMode,
                                     'j': cmdMove,
                                     'k': cmdMove,
                                     'h': cmdMove,
                                     'l': cmdMove,
                                     'w': cmdMove,
                                     'e': cmdMove,
                                     '$': cmdMove,
                                     '0': cmdMove,
                                     'x': cmdDelete,
                                     'A': cmdAppend,
                                    },
                          'composite': {'d': cmdCompositeDelete,
                                       }
                         },

                 INSERT: {'simple': {'\x1b': cmdNormalMode,  # ESC
                                    },
                          'composite': {}
                         }
                }
