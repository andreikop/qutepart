"""Autocompletion widget and logic
"""

import re

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QEvent, QModelIndex, QObject, QSize, Qt
from PyQt4.QtGui import QListView, QStyle

from qutepart.htmldelegate import HTMLDelegate


class _CompletionModel(QAbstractItemModel):
    """QAbstractItemModel implementation for a list of completion variants
    """
    def __init__(self, wordBeforeCursor, words, commonStart):
        QAbstractItemModel.__init__(self)
        
        self._typedText = wordBeforeCursor
        self._words = words

        self._canCompleteText = commonStart[len(wordBeforeCursor):]

    def plainText(self, rowIndex):
        """Get plain text of specified item
        """
        return self._words[rowIndex]

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
    
    def rowCount(self, index = QModelIndex()):
        """QAbstractItemModel method implementation
        """
        return len(self._words)
    
    def typedText(self):
        """Get current typed text
        """
        return self._typedText
    
    def words(self):
        """Return list of words
        """
        return self._words
    
    """Trivial QAbstractItemModel methods implementation
    """
    def flags(self, index):                                 return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    def headerData(self, index):                            return None
    def columnCount(self, index):                           return 1
    def index(self, row, column, parent = QModelIndex()):   return self.createIndex(row, column)
    def parent(self, index):                                return QModelIndex()


class _CompletionList(QListView):
    """Completion list widget
    """
    closeMe = pyqtSignal()
    itemSelected = pyqtSignal(int)
    
    def __init__(self, qpart, model):
        QListView.__init__(self, qpart.viewport())
        self.setItemDelegate(HTMLDelegate(self))
        
        self._qpart = qpart
        self.setModel(model)
        
        self._selectedIndex = -1
        
        qpart.installEventFilter(self)
        
        self.move(self._qpart.cursorRect().right() - self._horizontalShift(),
                  self._qpart.cursorRect().bottom())
        self.show()
        
        qpart.setFocus()
    
    def __del__(self):
        """Without this empty destructor Qt prints strange trace
            QObject::startTimer: QTimer can only be used with threads started with QThread
        when exiting
        """
        pass
    
    def del_(self):
        """Explicitly called destructor.
        Removes widget from the qpart
        """
        self.hide()
        self.setParent(None)
        # Now gc could collect me
    
    def sizeHint(self):
        """QWidget.sizeHint implementation
        Automatically resizes the widget according to rows count
        """
        width = max([self.fontMetrics().width(self.model().plainText(i)) \
                        for i in range(self.model().rowCount())])
        
        width += 4  # margin
        
        # drawn with scrollbar without +2. I don't know why
        height = self.sizeHintForRow(0) * self.model().rowCount() + 2
        
        return QSize(width, height)

    def _horizontalShift(self):
        """List should be plased such way, that typed text in the list is under
        typed text in the editor
        """
        strangeAdjustment = 2  # I don't know why. Probably, won't work on other systems and versions
        return self.fontMetrics().width(self.model().typedText()) + strangeAdjustment
    
    def eventFilter(self, object, event):
        """Catch events from qpart
        """
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape and \
               event.modifiers() == Qt.NoModifier:
                self.closeMe.emit()
            elif event.key() == Qt.Key_Down:
                if self._selectedIndex + 1 < self.model().rowCount():
                    self._selectItem(self._selectedIndex + 1)
                return True
            elif event.key() == Qt.Key_Up:
                if self._selectedIndex - 1 >= 0:
                    self._selectItem(self._selectedIndex - 1)
                return True
            elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if self._selectedIndex != -1:
                    self.itemSelected.emit(self._selectedIndex)
                    self._selectItem(self._selectedIndex - 1)
                    return True

        return super(QListView, self).eventFilter(object, event)

    def _selectItem(self, index):
        """Select item in the list
        """
        self._selectedIndex = index
        self.setCurrentIndex(self.model().createIndex(index, 0))

class Completer(QObject):
    """Object listens Qutepart widget events, computes and shows autocompletion lists
    """
    _wordPattern = "\w\w+"
    _wordRegExp = re.compile(_wordPattern)
    _wordAtEndRegExp = re.compile(_wordPattern + '$')
    
    def __init__(self, qpart):
        QObject.__init__(self, qpart)
        
        self._qpart = qpart
        self._widget = None
        
        qpart.installEventFilter(self)
    
    def __del__(self):
        """Close completion widget, if exists
        """
        self._closeCompletion()

    def eventFilter(self, object, event):
        """Catch events from qpart. Show completion if necessary
        """
        if event.type() == QEvent.KeyRelease:
            text = event.text()
            if text.isalpha() or text.isdigit() or text == '_':  # TODO take word separator characters from the parser
                ret = super(Completer, self).eventFilter(object, event)
                self._invokeCompletionIfAvailable()
                return ret
        
        return super(Completer, self).eventFilter(object, event)

    def _invokeCompletionIfAvailable(self):
        """Invoke completion, if available. Called after text has been typed in qpart
        """
        self._closeCompletion()
        
        wordBeforeCursor = self._wordBeforeCursor()
        if wordBeforeCursor is None:
            return
        
        words = self._makeListOfCompletions(wordBeforeCursor)
        if not words:
            return
        
        commonStart = self._commonWordStart(words)
        
        model = _CompletionModel(wordBeforeCursor, words, commonStart)
        
        self._widget = _CompletionList(self._qpart, model)
        self._widget.closeMe.connect(self._closeCompletion)
        self._widget.itemSelected.connect(self._onCompletionListItemSelected)

    def _closeCompletion(self):
        """Close completion, if visible.
        Delete widget
        """
        if self._widget is not None:
            self._widget.del_()
            self._widget = None
    
    def _wordBeforeCursor(self):
        """Get word, which is located before cursor
        """
        cursor = self._qpart.textCursor()
        textBeforeCursor = cursor.block().text()[:cursor.position() - cursor.block().position()]
        match = self._wordAtEndRegExp.search(textBeforeCursor)
        if match:
            return match.group(0)
        else:
            return None
    
    def _makeWordSet(self):
        """Make a set of words, which shall be completed, from text
        """
        return set(self._wordRegExp.findall(self._qpart.toPlainText()))

    def _makeListOfCompletions(self, wordBeforeCursor):
        """Make list of completions, which shall be shown
        """
        allWords = self._makeWordSet()
        onlySuitable = [word for word in allWords \
                                if word.startswith(wordBeforeCursor) and \
                                   word != wordBeforeCursor]
        
        return sorted(onlySuitable)
    
    def _commonWordStart(self, words):
        """Get common start of all words.
        i.e. for ['blablaxxx', 'blablayyy', 'blazzz'] common start is 'bla'
        """
        if not words:
            return ''
        
        length = 0
        firstWord = words[0]
        otherWords = words[1:]
        for index, char in enumerate(firstWord):
            if not all([word[index] == char for word in otherWords]):
                break
            length = index + 1
        
        return firstWord[:length]
    
    def _onCompletionListItemSelected(self, index):
        """Item selected. Insert completion to editor
        """
        model = self._widget.model()
        selectedWord = model.words()[index]
        textToInsert = selectedWord[len(model.typedText()):]
        self._qpart.textCursor().insertText(textToInsert)
        self._closeCompletion()
