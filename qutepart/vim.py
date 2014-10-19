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

    def isActive(self):
        return True

    def indication(self):
        return MODE_COLORS[self._mode], self._mode

    def keyPressEvent(self, event):
        """Check the event. Return True if processed and False otherwise
        """
        simpleCommands = self._COMMANDS[self._mode]['simple']
        compositeCommands = self._COMMANDS[self._mode]['composite']

        if event.text() in simpleCommands:
            cmdFunc = simpleCommands[event.text()]
            cmdFunc(self)
            return True
        else:
            return False

    def _move(self, direction):
        cursor = self._qpart.textCursor()
        cursor.movePosition(direction)
        self._qpart.setTextCursor(cursor)

    def cmdDown(self):  self._move(QTextCursor.Down)
    def cmdUp(self):    self._move(QTextCursor.Up)
    def cmdLeft(self):  self._move(QTextCursor.Left)
    def cmdRight(self): self._move(QTextCursor.Right)

    def _setMode(self, mode):
        self._mode = mode
        self.modeIndicationChanged.emit(MODE_COLORS[mode], mode)

    def cmdInsertMode(self): self._setMode(INSERT)
    def cmdNormalMode(self): self._setMode(NORMAL)

    def cmdDelete(self):
        self._qpart.textCursor().deleteChar()

    def cmdWaitDelete(self):
        self._pendingCmd = 'd'

    _COMMANDS = {NORMAL: {'simple': {'i': cmdInsertMode,
                                     'j': cmdDown,
                                     'k': cmdUp,
                                     'h': cmdLeft,
                                     'l': cmdRight,
                                     'x': cmdDelete,
                                    },
                          'composite': {
                                       }
                         },

                 INSERT: {'simple': {'\x1b': cmdNormalMode,  # ESC
                                    },
                          'composite': {}
                         }
                }

