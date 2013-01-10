"""Autocompletion widget and logic
"""

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QObject, QSize, Qt
from PyQt4.QtGui import QListView, QStyle

from qutepart.htmldelegate import HTMLDelegate


class _CompletionModel(QAbstractItemModel):
    """QAbstractItemModel implementation for a list of completion variants
    """
    def __init__(self):
        QAbstractItemModel.__init__(self)
        
        self._typedText = 'veeeeeeeery long test d'
        self._canCompleteText = 'ata'
        

    def plainText(self, rowIndex):
        """Get plain text of specified item
        """
        return "veeeeeeeery long test data value"

    def data(self, index, role = Qt.DisplayRole):
        """QAbstractItemModel method implementation
        """
        if role == Qt.DisplayRole:
            text = self.plainText(index.row())
            typed = text[:len(self._typedText)]
            canComplete = text[len(self._typedText):len(self._typedText) + len(self._canCompleteText)]
            rest = text[len(self._typedText) + len(self._canCompleteText):]
            return '<html>' \
                           '%s' \
                        '<b>%s</b>' \
                           '%s' \
                    '</html>' % (typed, canComplete, rest)
        else:
            return None
    
    def rowCount(self, index):
        """QAbstractItemModel method implementation
        """
        return 7
    
    def typedText(self):
        """Get current typed text
        """
        return self._typedText
    
    """Trivial QAbstractItemModel methods implementation
    """
    def flags(self, index):                                 return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    def headerData(self, index):                            return None
    def columnCount(self, index):                           return 1
    def index(self, row, column, parent = QModelIndex()):   return self.createIndex(row, column)
    def parent(self, index):                                return QModelIndex()


class _ListView(QListView):
    """Completion list widget
    """
    def __init__(self, qpart, model):
        QListView.__init__(self, qpart.viewport())
        self.setItemDelegate(HTMLDelegate(self))
        self.setFont(qpart.font())
        
        qpart.setFocus()
        
        self._qpart = qpart
        self.setModel(model)
        
        qpart.cursorPositionChanged.connect(self._onCursorPositionChanged)
    
    def __del__(self):
        """Without this empty destructor Qt prints strange trace
            QObject::startTimer: QTimer can only be used with threads started with QThread
        when exiting
        """
        pass
    
    def _onCursorPositionChanged(self):
        """Cursor position changed. Update completion widget position
        """
        self.move(self._qpart.cursorRect().right() - self._horizontalShift(),
                  self._qpart.cursorRect().bottom())
    
    def sizeHint(self):
        """QWidget.sizeHint implementation
        Automatically resizes the widget according to rows count
        """
        width = max([self.fontMetrics().width(self.model().plainText(i)) \
                        for i in range(self.model().rowCount(QModelIndex()))])
        
        width += 4  # margin
        
        # drawn with scrollbar without +2. I don't know why
        height = self.sizeHintForRow(0) * self.model().rowCount(QModelIndex()) + 2
        
        return QSize(width, height)

    def _horizontalShift(self):
        """List should be plased such way, that typed text in the list is under
        typed text in the editor
        """
        strangeAdjustment = 2  # I don't know why. Probably, won't work on other systems and versions
        return self.fontMetrics().width(self.model().typedText()) + strangeAdjustment


class Completer(QObject):
    """Object listens Qutepart widget events, computes and shows autocompletion lists
    """
    def __init__(self, qpart):
        self._qpart = qpart
        
        self._widget = _ListView(qpart, _CompletionModel())
        self._widget.show()

