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
        simpleCommands = self._COMMANDS[self._mode]['simple']
        compositeCommands = self._COMMANDS[self._mode]['composite']

        if self._pendingCmd:
            cmdFunc = self._COMMANDS[self._mode]['composite'][self._pendingCmd]
            cmdFunc(self, self._pendingCmd, event.text())
            self._pendingCmd = None
            return True
        elif event.text() in simpleCommands:
            cmdFunc = simpleCommands[event.text()]
            cmdFunc(self, event.text())
            return True
        elif event.text() in compositeCommands:
            self._pendingCmd = event.text()
            return True
        else:
            return False

    def _moveCursor(self, motion, select=False):
        cursor = self._qpart.textCursor()

        moveMode = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor

        if motion == 'j':
            cursor.movePosition(QTextCursor.Down, moveMode)
        elif motion == 'k':
            cursor.movePosition(QTextCursor.Up, moveMode)
        elif motion == 'h':
            cursor.movePosition(QTextCursor.Left, moveMode)
        elif motion == 'l':
            cursor.movePosition(QTextCursor.Right, moveMode)

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
        self._moveCursor(motion, select=True)
        self._qpart.textCursor().removeSelectedText()

    _COMMANDS = {NORMAL: {'simple': {'i': cmdInsertMode,
                                     'j': cmdMove,
                                     'k': cmdMove,
                                     'h': cmdMove,
                                     'l': cmdMove,
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
