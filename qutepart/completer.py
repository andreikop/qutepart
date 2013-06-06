"""Autocompletion widget and logic
"""

import re

from PyQt4.QtCore import pyqtSignal, QAbstractItemModel, QEvent, QModelIndex, QObject, QSize, Qt, QTimer
from PyQt4.QtGui import QCursor, QListView, QStyle

from qutepart.htmldelegate import HTMLDelegate


class _CompletionModel(QAbstractItemModel):
    """QAbstractItemModel implementation for a list of completion variants
    
    words attribute contains all words
    canCompleteText attribute contains text, which may be inserted with tab
    """
    def __init__(self, wordBeforeCursor, words, commonStart):
        QAbstractItemModel.__init__(self)
        
        self._setData(wordBeforeCursor, words, commonStart)

    def _setData(self, wordBeforeCursor, words, commonStart):
        """Set model information
        """
        self._typedText = wordBeforeCursor
        self.words = words
        self.canCompleteText = commonStart[len(wordBeforeCursor):]
        
        self.layoutChanged.emit()

    def updateData(self, wordBeforeCursor, words, commonStart):
        """Set model information
        """
        self._setData(wordBeforeCursor, words, commonStart)
        self.layoutChanged.emit()

    def data(self, index, role):
        """QAbstractItemModel method implementation
        """
        if role == Qt.DisplayRole:
            text = self.words[index.row()]
            typed = text[:len(self._typedText)]
            canComplete = text[len(self._typedText):len(self._typedText) + len(self.canCompleteText)]
            rest = text[len(self._typedText) + len(self.canCompleteText):]
            if canComplete:
                # NOTE foreground colors are hardcoded, but I can't set background color of selected item (Qt bug?)
                # might look bad on some color themes
                return '<html>' \
                            '<font color="#000000">%s</font>' \
                            '<font color="#e80000">%s</font>' \
                            '<font color="#000000">%s</font>' \
                        '</html>' % (typed, canComplete, rest)
            else:
                return typed + rest
        else:
            return None
    
    def rowCount(self, index = QModelIndex()):
        """QAbstractItemModel method implementation
        """
        return len(self.words)
    
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


class _CompletionList(QListView):
    """Completion list widget
    """
    closeMe = pyqtSignal()
    itemSelected = pyqtSignal(int)
    tabPressed = pyqtSignal()
    
    _MAX_VISIBLE_ROWS = 20  # no any technical reason, just for better UI
    
    _ROW_MARGIN = 6
    
    def __init__(self, qpart, model):
        QListView.__init__(self, qpart.viewport())
        self.setItemDelegate(HTMLDelegate(self))
        
        self._qpart = qpart
        self.setFont(qpart.font())
        
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.setModel(model)
        
        self._selectedIndex = -1
        
        # if cursor moved, we shall close widget, if its position (and model) hasn't been updated
        self._closeIfNotUpdatedTimer = QTimer()
        self._closeIfNotUpdatedTimer.setInterval(200)
        self._closeIfNotUpdatedTimer.setSingleShot(True)

        self._closeIfNotUpdatedTimer.timeout.connect(self._afterCursorPositionChanged)
        
        qpart.installEventFilter(self)
        
        qpart.cursorPositionChanged.connect(self._onCursorPositionChanged)
        
        self.clicked.connect(lambda index: self.itemSelected.emit(index.row()))
        
        self.updateGeometry()
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
        self._closeIfNotUpdatedTimer.stop()
        self._qpart.removeEventFilter(self)
        self._qpart.cursorPositionChanged.disconnect(self._onCursorPositionChanged)
        
        # if object is deleted synchronously, Qt crashes after it on events handling
        QTimer.singleShot(0, lambda: self.setParent(None))

    def sizeHint(self):
        """QWidget.sizeHint implementation
        Automatically resizes the widget according to rows count
        
        FIXME very bad algorithm. Remove all this margins, if you can
        """
        width = max([self.fontMetrics().width(word) \
                        for word in self.model().words])
        width = width * 1.4  # FIXME bad hack. invent better formula
        width += 30  # margin
        
        # drawn with scrollbar without +2. I don't know why
        rowCount = min(self.model().rowCount(), self._MAX_VISIBLE_ROWS)
        height = (self.sizeHintForRow(0) * rowCount) + self._ROW_MARGIN

        return QSize(width, height)

    def minimumHeight(self):
        """QWidget.minimumSizeHint implementation
        """
        return self.sizeHintForRow(0) + self._ROW_MARGIN

    def _horizontalShift(self):
        """List should be plased such way, that typed text in the list is under
        typed text in the editor
        """
        strangeAdjustment = 2  # I don't know why. Probably, won't work on other systems and versions
        return self.fontMetrics().width(self.model().typedText()) + strangeAdjustment

    def updateGeometry(self):
        """Move widget to point under cursor
        """
        WIDGET_BORDER_MARGIN = 5
        SCROLLBAR_WIDTH = 30  # just a guess
        
        sizeHint = self.sizeHint()
        width = sizeHint.width()
        height = sizeHint.height()

        cursorRect = self._qpart.cursorRect()
        parentSize = self.parentWidget().size()
        
        spaceBelow = parentSize.height() - cursorRect.bottom() - WIDGET_BORDER_MARGIN
        spaceAbove = cursorRect.top() - WIDGET_BORDER_MARGIN
        
        if height <= spaceBelow or \
           spaceBelow > spaceAbove:
            yPos = cursorRect.bottom()
            if height > spaceBelow and \
               spaceBelow > self.minimumHeight():
                height = spaceBelow
                width = width + SCROLLBAR_WIDTH
        else:
            if height > spaceAbove and \
               spaceAbove > self.minimumHeight():
                height = spaceAbove
                width = width + SCROLLBAR_WIDTH
            yPos = cursorRect.top() - height

        xPos = cursorRect.right() - self._horizontalShift()
        
        if xPos + width + WIDGET_BORDER_MARGIN > parentSize.width():
            xPos = parentSize.width() - WIDGET_BORDER_MARGIN - width
        
        self.setGeometry(xPos, yPos, width, height)
        self._closeIfNotUpdatedTimer.stop()
    
    def _onCursorPositionChanged(self):
        """Cursor position changed. Schedule closing.
        Timer will be stopped, if widget position is being updated
        """
        self._closeIfNotUpdatedTimer.start()

    def _afterCursorPositionChanged(self):
        """Widget position hasn't been updated after cursor position change, close widget
        """
        self.closeMe.emit()

    def eventFilter(self, object, event):
        """Catch events from qpart
        Move selection, select item, or close themselves
        """
        if event.type() == QEvent.KeyPress and event.modifiers() == Qt.NoModifier:
            if event.key() == Qt.Key_Escape:
                self.closeMe.emit()
                return True
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
                    return True
            elif event.key() == Qt.Key_Tab:
                self.tabPressed.emit()
                return True
        elif event.type() == QEvent.FocusOut:
            self.closeMe.emit()

        return False

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
    _wordAtStartRegExp = re.compile('^' + _wordPattern)
    
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
            textTyped = (event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier)) and \
                        (text.isalpha() or text.isdigit() or text == '_')
            
            if textTyped or \
            (event.key() == Qt.Key_Backspace and self._widget is not None):
                self._invokeCompletionIfAvailable()
                return False
        
        return False

    def _invokeCompletionIfAvailable(self):
        """Invoke completion, if available. Called after text has been typed in qpart
        """
        if not self._qpart.completionEnabled:
            self._closeCompletion()
            return
        
        wordBeforeCursor = self._wordBeforeCursor()
        if not wordBeforeCursor:
            self._closeCompletion()
            return
        
        if len(wordBeforeCursor) < self._qpart.completionThreshold:
            self._closeCompletion()
            return
        
        words = self._makeListOfCompletions(wordBeforeCursor)
        if not words:
            self._closeCompletion()
            return
        
        commonStart = self._commonWordStart(words)
        
        if self._widget is None:
            model = _CompletionModel(wordBeforeCursor, words, commonStart)
            self._widget = _CompletionList(self._qpart, model)
            self._widget.closeMe.connect(self._closeCompletion)
            self._widget.itemSelected.connect(self._onCompletionListItemSelected)
            self._widget.tabPressed.connect(self._onCompletionListTabPressed)
        else:
            self._widget.model().updateData(wordBeforeCursor, words, commonStart)
            self._widget.updateGeometry()

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
        textBeforeCursor = cursor.block().text()[:cursor.positionInBlock()]
        match = self._wordAtEndRegExp.search(textBeforeCursor)
        if match:
            return match.group(0)
        else:
            return ''
    
    def _wordAfterCursor(self):
        """Get word, which is located before cursor
        """
        cursor = self._qpart.textCursor()
        textAfterCursor = cursor.block().text()[cursor.positionInBlock():]
        match = self._wordAtStartRegExp.search(textAfterCursor)
        if match:
            return match.group(0)
        else:
            return ''
    
    def _makeWordSet(self):
        """Make a set of words, which shall be completed, from text
        """
        return set(self._wordRegExp.findall(self._qpart.toPlainText()))

    def _makeListOfCompletions(self, wordBeforeCursor):
        """Make list of completions, which shall be shown
        """
        wholeWord = wordBeforeCursor + self._wordAfterCursor()
        allWords = self._makeWordSet()
        onlySuitable = [word for word in allWords \
                                if word.startswith(wordBeforeCursor) and \
                                   word != wholeWord]
        
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
        selectedWord = model.words[index]
        textToInsert = selectedWord[len(model.typedText()):]
        self._qpart.textCursor().insertText(textToInsert)
        self._closeCompletion()

    def _onCompletionListTabPressed(self):
        """Tab pressed on completion list
        Insert completable text, if available
        """
        canCompleteText = self._widget.model().canCompleteText
        if canCompleteText:
            self._qpart.textCursor().insertText(canCompleteText)
            self._invokeCompletionIfAvailable()
