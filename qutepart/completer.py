"""Autocompletion widget and logic
"""

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QObject, QSize, Qt
from PyQt4.QtGui import QListView, QStyle, QStyledItemDelegate

class _CompletionModel(QAbstractItemModel):
    """QAbstractItemModel implementation for a list of completion variants
    """
    def __init__(self):
        QObject.__init__(self)

    def flags(self, index):
        """QAbstractItemModel method implementation
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def data(self, index, role):
        """QAbstractItemModel method implementation
        """
        if role == Qt.DisplayRole:
            return "test data"
        else:
            return None
        
    def headerData(self, index):
        """QAbstractItemModel method implementation
        """
        return "the header"
    
    def rowCount(self, index):
        """QAbstractItemModel method implementation
        """
        return 7
    
    def columnCount(self, index):
        """QAbstractItemModel method implementation
        """
        return 1
    
    def index(self, row, column, parent = QModelIndex()):
        """QAbstractItemModel method implementation
        """
        return self.createIndex(row, column)
    
    def parent(self, index):
        """QAbstractItemModel method implementation
        """
        return QModelIndex()


class _StyledItemDelegate(QStyledItemDelegate):
    """Draw QListView items without dotted focus frame
    http://qt-project.org/faq/answer/how_can_i_remove_the_dotted_rectangle_from_the_cell_that_has_focus_in_my_qt
    """
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)
        
    def paint(self, painter, option, index):
        opt = option
        opt.state &= ~QStyle.State_HasFocus
        QStyledItemDelegate.paint(self, painter, opt, index)


class _ListView(QListView):
    """Completion list widget
    """
    def __init__(self, qpart, model):
        QListView.__init__(self, qpart.viewport())
        self.setItemDelegate(_StyledItemDelegate(self))
        
        self._qpart = qpart
        self.setModel(model)
        
        
        qpart.cursorPositionChanged.connect(self._onCursorPositionChanged)
    
    def _onCursorPositionChanged(self):
        """Cursor position changed. Update completion widget position
        """
        self.move(self._qpart.cursorRect().bottomRight())
    
    def sizeHint(self):
        """QWidget.sizeHint implementation
        Automatically resizes the widget according to rows count
        """
        width = super(_ListView, self).sizeHint().width()
        
        # drawn with scrollbar without +2. I don't know why
        height = self.sizeHintForRow(0) * self.model().rowCount(QModelIndex()) + 2
        
        return QSize(width, height)


class Completer(QObject):
    """Object listens Qutepart widget events, computes and shows autocompletion lists
    """
    def __init__(self, qpart):
        self._qpart = qpart
        
        self._widget = _ListView(qpart, _CompletionModel())
        self._widget.show()

