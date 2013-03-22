"""qutepart --- Code editor component for PyQt and Pyside
=========================================================
"""

import os.path
import logging

from PyQt4.QtCore import QRect, Qt, pyqtSignal
from PyQt4.QtGui import QAction, QApplication, QColor, QBrush, QFont, QIcon, QKeySequence, QPainter, QPalette, QPlainTextEdit, \
                        QPixmap, QShortcut, QTextCharFormat, QTextCursor, QTextEdit, QTextFormat, QWidget

from qutepart.syntax import SyntaxManager
from qutepart.syntaxhlighter import SyntaxHighlighter
from qutepart.brackethlighter import BracketHighlighter
from qutepart.indenter import getIndenter
from qutepart.completer import Completer
from qutepart.lines import Lines


logger = logging.getLogger('qutepart')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter("qutepart: %(message)s"))
logger.addHandler(consoleHandler)


_ICONS_PATH = os.path.join(os.path.dirname(__file__), 'icons')

def _getIconPath(iconFileName):
    return os.path.join(_ICONS_PATH, iconFileName)


#Define for old Qt versions method, which appeared in 4.7
if not hasattr(QTextCursor, 'positionInBlock'):
    def _positionInBlock(cursor):
        return cursor.position() - cursor.block().position()
    QTextCursor.positionInBlock = _positionInBlock

# Helper method, not supported by Qt
if not hasattr(QTextCursor, 'setPositionInBlock'):
    if not hasattr(QTextCursor, 'MoveAnchor'):  # using a mock, avoiding crash. See doc/source/conf.py
        QTextCursor.MoveAnchor = None
    def _setPositionInBlock(cursor, positionInBlock, anchor=QTextCursor.MoveAnchor):
        return cursor.setPosition(cursor.block().position() + positionInBlock, anchor)
    QTextCursor.setPositionInBlock = _setPositionInBlock


class _Bookmarks:
    """Bookmarks functionality implementation, grouped in one class
    """
    def __init__(self, qpart, markArea):
        self._qpart = qpart
        self._markArea = markArea
        qpart.toggleBookmark = self._createAction(qpart, "bookmark.png", "Toogle bookmark", 'Ctrl+B', self._onToggleBookmark)
        qpart.nextBookmark = self._createAction(qpart, "up.png", "Previous bookmark", 'Alt+PgUp', self._onPrevBookmark)
        qpart.prevBookmark = self._createAction(qpart, "down.png", "Next bookmark", 'Alt+PgDown', self._onNextBookmark)

    def _createAction(self, widget, iconFileName, text, shortcut, slot):
        """Create QAction with given parameters and add to the widget
        """
        icon = QIcon(_getIconPath(iconFileName))
        action = QAction(icon, text, widget)
        action.setShortcut(QKeySequence(shortcut))
        action.setShortcutContext(Qt.WidgetShortcut)
        action.triggered.connect(slot)
        
        widget.addAction(action)
        
        return action

    def clear(self, startBlock, endBlock):
        """Clear bookmarks on block range including start and end
        """
        for block in iterateBlocksFrom(startBlock):
            self._setBlockMarked(block, False)
            if block == endBlock:
                break

    @staticmethod
    def isBlockMarked(block):
        """Check if block is bookmarked
        """
        return block.userState() == 1

    def _setBlockMarked(self, block, marked):
        """Set block bookmarked
        """
        block.setUserState(1 if marked else -1)
    
    def _onToggleBookmark(self):
        """Toogle Bookmark action triggered
        """
        block = self._qpart.textCursor().block()
        self._setBlockMarked(block, not self.isBlockMarked(block))
        self._markArea.update()
    
    def _onPrevBookmark(self):
        """Previous Bookmark action triggered. Move cursor
        """
        for block in iterateBlocksBackFrom(self._qpart.textCursor().block().previous()):
            if self.isBlockMarked(block):
                self._qpart.setTextCursor(QTextCursor(block))
                return
    
    def _onNextBookmark(self):
        """Previous Bookmark action triggered. Move cursor
        """
        for block in iterateBlocksFrom(self._qpart.textCursor().block().next()):
            if self.isBlockMarked(block):
                self._qpart.setTextCursor(QTextCursor(block))
                return


class _LineNumberArea(QWidget):
    """Line number area widget
    """
    _LEFT_MARGIN = 3
    _RIGHT_MARGIN = 3
    
    def __init__(self, qpart):
        QWidget.__init__(self, qpart)
        self._qpart = qpart
    
    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
        painter.setPen(Qt.black)

        block = self._qpart.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset()).top())
        bottom = top + int(self._qpart.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.drawText(0, top, self.width() - self._RIGHT_MARGIN, self._qpart.fontMetrics().height(),
                                 Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self._qpart.blockBoundingRect(block).height())
            blockNumber += 1

    def width(self):
        """Desired width. Includes text and margins
        """
        digits = len(str(max(1, self._qpart.blockCount())))

        return self._LEFT_MARGIN + self._qpart.fontMetrics().width('9') * digits + self._RIGHT_MARGIN


class _MarkArea(QWidget):
    
    _MARGIN = 1
    
    def __init__(self, qpart):
        QWidget.__init__(self, qpart)
        self._qpart = qpart
        
        qpart.blockCountChanged.connect(self.update)
        
        defaultSizePixmap = QPixmap(_getIconPath('bookmark.png'))
        iconSize = self._qpart.cursorRect().height()
        self._bookmarkPixmap = defaultSizePixmap.scaled(iconSize, iconSize)
    
    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        Draw markers
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))

        block = self._qpart.firstVisibleBlock()
        blockBoundingGeometry = self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset())
        top = blockBoundingGeometry.top()
        bottom = top + blockBoundingGeometry.height()
        
        for block in iterateBlocksFrom(block):
            if top > event.rect().bottom():
                break
            if block.isVisible() and \
               bottom >= event.rect().top() and \
               _Bookmarks.isBlockMarked(block):
                painter.drawPixmap(0, top, self._bookmarkPixmap)
            
            top += self._qpart.blockBoundingGeometry(block).height()

    def width(self):
        """Desired width. Includes text and margins
        """
        return self._MARGIN + self._bookmarkPixmap.width() + self._MARGIN


class Qutepart(QPlainTextEdit):
    '''Qutepart is based on QPlainTextEdit, and you can use QPlainTextEdit methods,
    if you don't see some functionality here.
    
    **Text**
    
    ``text`` attribute holds current text. It may be read and written.::
    
        qpart.text = readFile()
        saveFile(qpart.text)
    
    This attribute always returns text, separated with ``\n``. Use textForSaving() for get original text.
    
    It is recommended to use ``lines`` attribute whenever possible,
    because access to ``text`` might require long time on big files.
    Attribute is cached, only first read access after text has been changed in slow.
    
    **Selected text**
    
    ``selectedText`` attribute holds selected text. It may be read and written.
    Write operation replaces selection with new text. If nothing is selected - just inserts text::

        print qpart.selectedText  # print selection
        qpart.selectedText = 'new text'  # replace selection
    
    **Text lines**
    
    ``lines`` attribute, which represents text as list-of-strings like object
    and allows to modify it. Examples::
    
        qpart.lines[0]  # get the first line of the text
        qpart.lines[-1]  # get the last line of the text
        qpart.lines[2] = 'new text'  # replace 3rd line value with 'new text'
        qpart.lines[1:4]  # get 3 lines of text starting from the second line as list of strings
        qpart.lines[1:4] = ['new line 2', 'new line3', 'new line 4']  # replace value of 3 lines
        del qpart.lines[3]  # delete 4th line
        del qpart.lines[3:5]  # delete lines 4, 5, 6
        
        len(qpart.lines)  # get line count
        
        qpart.lines.append('new line')  # append new line to the end
        qpart.lines.insert(1, 'new line')  # insert new line before line 1
        
        print qpart.lines  # print all text as list of strings
        
        # iterate over lines.
        for lineText in qpart.lines:
            doSomething(lineText)
        
        qpart.lines = ['one', 'thow', 'three']  # replace whole text

    ``cursorPosition`` cursor position as ``(line, column)``. Lines are numerated from zero. If column is set to ``None`` - cursor will be placed before first non-whitespace character
    ``absCursorPosition`` cursor position as offset from the beginning of text.
    ``selectedPosition`` selection coordinates as ``((startLine, startCol), (cursorLine, cursorCol))``.
    ``absSelectedPosition`` selection coordinates as ``(startPosition, cursorPosition)`` where position is offset from the beginning of text.
    ``eol`` End Of Line character. Supported values are ``\n``, ``\r``, ``\r\n``. See comments for ``textForSaving()``
    ``indentWidth`` Width of Tab character, and width of one indentation level
    ``indentUseTabs`` If True, Tab character inserts Tab, otherwise - spaces


    **Actions**
    
    Component contains list of actions (QAction instances).
    Actions can be insered to some menu, a shortcut and an icon can be configured. List of actions:
    
    * ``toggleBookmark`` - Set/Clear bookmark on current block
    * ``nextBookmark`` - Jump to next bookmark
    * ``prevBookmark`` - Jump to previous bookmark
    
    **Text modification and Undo/Redo**
    
    Sometimes, it is required to make few text modifications, which are Undo-Redoble as atomic operation.
    i.e. you want to indent (insert indentation) few lines of text, but user shall be able to
    Undo it in one step. In this case, you can use Qutepart as a context manager.::
    
        with qpart:
            qpart.modifySomeText()
            qpart.modifyOtherText()
    
    Nested atomic operations are joined in one operation
    
    ***Signals***
    
    ``languageChanged``` Language has changed. See also ``language()``
    ``indentWidthChanged(int)`` Indentation width changed. See also ``indentWidth``
    ``indentUseTabsChanged(bool)`` Indentation uses tab property changed. See also ``indentUseTabs``
    '''
    
    languageChanged = pyqtSignal(unicode)
    indentWidthChanged = pyqtSignal(int)
    indentUseTabsChanged = pyqtSignal(bool)
    
    _DEFAULT_EOL = '\n'
    _DEFAULT_INDENT_WIDTH = 4
    _DEFAULT_INDENT_USE_TABS = False
    
    _COMPLETION_THRESHOLD = 3
    
    _globalSyntaxManager = SyntaxManager()
    
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        
        # toPlainText() takes a lot of time on long texts, therefore it is cached
        self._cachedText = None
        
        self._eol = self._DEFAULT_EOL
        self._indentWidth = self._DEFAULT_INDENT_WIDTH
        self._indentUseTabs = self._DEFAULT_INDENT_USE_TABS
        self._atomicModificationDepth = 0

        self.setFont(QFont("Monospace"))
        
        self._highlighter = None
        self._bracketHighlighter = BracketHighlighter()
        
        self._indenter = getIndenter('normal', self)
        
        self._lines = Lines(self)
        
        self._initShortcuts()
        
        self._completer = Completer(self)
        
        self._lineNumberArea = _LineNumberArea(self)
        self._countCache = (-1, -1)
        self._markArea = _MarkArea(self)
        
        self._bookmarks = _Bookmarks(self, self._markArea)
        
        self._userExtraSelections = []  # we draw bracket highlighting, current line and extra selections by user
        self._userExtraSelectionFormat = QTextCharFormat()
        self._userExtraSelectionFormat.setBackground(QBrush(QColor('#ffee00')))

        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateSideAreas)
        self.cursorPositionChanged.connect(self._updateExtraSelections)
        self.textChanged.connect(lambda: self.setExtraSelections([]))  # drop user extra selections
        self.textChanged.connect(self._resetCachedText)

        self._updateLineNumberAreaWidth(0)
        self._updateExtraSelections()
    
    def _initShortcuts(self):
        """Init shortcuts for text editing
        """
        def createShortcut(keySeq, slot):
            shortcut = QShortcut(QKeySequence(keySeq), self)
            shortcut.setContext(Qt.WidgetShortcut)
            shortcut.activated.connect(slot)
        
        createShortcut('Ctrl+Up', lambda: self._onShortcutScroll(down = False))
        createShortcut('Ctrl+Down', lambda: self._onShortcutScroll(down = True))
        createShortcut('Ctrl+Shift+Up', lambda: self._onShortcutSelectAndScroll(down = False))
        createShortcut('Ctrl+Shift+Down', lambda: self._onShortcutSelectAndScroll(down = True))
        createShortcut('Shift+Tab', lambda: self._onShortcutChangeSelectedBlocksIndentation(increase = False))
        createShortcut('Alt+Up', lambda: self._onShortcutMoveLine(down = False))
        createShortcut('Alt+Down', lambda: self._onShortcutMoveLine(down = True))
        createShortcut('Alt+Del', self._onShortcutDeleteLine)
        createShortcut('Alt+C', self._onShortcutCopyLine)
        createShortcut('Alt+V', self._onShortcutPasteLine)
        createShortcut('Alt+X', self._onShortcutCutLine)
        createShortcut('Alt+D', self._onShortcutDuplicateLine)
        createShortcut('Ctrl+I', self._onShortcutAutoIndentSelection)

    def __enter__(self):
        """Context management method.
        Begin atomic modification
        """
        self._atomicModificationDepth = self._atomicModificationDepth + 1
        if self._atomicModificationDepth == 1:
            self.textCursor().beginEditBlock()
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context management method.
        End atomic modification
        """
        self._atomicModificationDepth = self._atomicModificationDepth - 1
        if self._atomicModificationDepth == 0:
            self.textCursor().endEditBlock()
        
        if exc_type is not None:
            return False

    def setFont(self, font):
        pass # suppress dockstring for non-public method
        """Set font and update tab stop width
        """
        QPlainTextEdit.setFont(self, font)
        self._updateTabStopWidth()
    
    def _updateTabStopWidth(self):
        """Update tabstop width after font or indentation changed
        """
        self.setTabStopWidth(self.fontMetrics().width(' ' * self._indentWidth))
    
    @property
    def lines(self):
        return self._lines
    
    @lines.setter
    def lines(self, value):
        if not isinstance(value, (list, tuple)) or \
           not all([isinstance(item, basestring) for item in value]):
            raise TypeError('Invalid new value of "lines" attribute')
        self.setPlainText('\n'.join(value))

    def _resetCachedText(self):
        """Reset toPlainText() result cache
        """
        self._cachedText = None
    
    @property
    def text(self):
        if self._cachedText is None:
            self._cachedText = self.toPlainText()
        
        return self._cachedText
    
    @text.setter
    def text(self, text):
        self.setPlainText(text)
    
    def textForSaving(self):
        """Get text with correct EOL symbols. Use this method for saving a file to storage
        """
        return self.eol.join(self.text.splitlines())
    
    @property
    def selectedText(self):
        return self.textCursor().selectedText()
    
    @selectedText.setter
    def selectedText(self, text):
        self.textCursor().insertText(text)
    
    @property
    def cursorPosition(self):
        cursor = self.textCursor()
        return cursor.block().blockNumber(), cursor.positionInBlock()
    
    @cursorPosition.setter
    def cursorPosition(self, pos):
        line, col = pos
        
        line = min(line, len(self.lines) - 1)
        lineText = self.lines[line]
        
        if col is not None:
            col = min(col, len(lineText))
        else:
            col = len(lineText) - len(lineText.lstrip())
        
        block = QTextCursor(self.document().findBlockByNumber(line))
        cursor = QTextCursor(block)
        cursor.setPositionInBlock(col)
        self.setTextCursor(cursor)
    
    @property
    def absCursorPosition(self):
        return self.textCursor().position()
    
    @absCursorPosition.setter
    def absCursorPosition(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
    
    @property
    def selectedPosition(self):
        cursor = self.textCursor()
        cursorLine, cursorPos = cursor.blockNumber(), cursor.positionInBlock()
    
        cursor.setPosition(cursor.anchor())
        startLine, startCol = cursor.blockNumber(), cursor.positionInBlock()
        
        return ((startLine, startCol), (cursorLine, cursorCol))

    @selectedPosition.setter
    def selectedPosition(self, pos):
        anchorPos, cursorPos = pos
        anchorLine, anchorCol = anchorPos
        cursorLine, cursorCol = cursorPos
        
        anchorCursor = self.document().findBlockByNumber(anchorLine)
        anchorCursor.setPositionInBlock(anchorCol)
        
        # just get absolute position
        cursor = self.document().findBlockByNumber(cursorLine)
        cursor.setPositionInBlock(cursorCol)
        
        anchorCursor.setPosition(cursor.position(), Qt.KeepAnchor)
        self.setTextCursor(cursor)
    
    @property
    def absSelectedPosition(self):
        cursor = self.textCursor()
        return cursor.anchor(), cursor.position()
    
    @absSelectedPosition.setter
    def absSelectedPosition(self, pos):
        anchorPos, cursorPos = pos
        cursor = self.textCursor()
        cursor.setPosition(anchorPos)
        cursor.setPosition(cursorPos, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
    
    def resetSelection(self):
        """Reset selection. Nothing will be selected.
        """
        cursor = self.textCursor()
        cursor.setPosition(cursor.position())
        self.setTextCursor(cursor)

    @property
    def eol(self):
        return self._eol
    
    @eol.setter
    def eol(self, eol):
        if not eol in ('\r', '\n', '\r\n'):
            raise ValueError("Invalid EOL value")
        if eol != self._eol:
            self._eol = eol

    @property
    def indentWidth(self):
        return self._indentWidth
    
    @indentWidth.setter
    def indentWidth(self, width):
        if self._indentWidth != width:
            self._indentWidth = width
            self._updateTabStopWidth()
            self.indentWidthChanged.emit(width)
    
    @property
    def indentUseTabs(self):
        return self._indentUseTabs
    
    @indentUseTabs.setter
    def indentUseTabs(self, use):
        if use != self._indentUseTabs:
            self._indentUseTabs = use
            self.indentUseTabsChanged.emit(use)
    
    def _indentText(self):
        """Get indent text as \t or string of spaces
        """
        if self._indentUseTabs:
            return '\t'
        else:
            return ' ' * self._indentWidth
    
    def replaceText(self, pos, length, text):
        """Replace length symbols from (line, col) with new text.
        
        If ``pos`` is an integer, it is interpreted as absolute position, if a tuple - as ``(line, column)``
        """
        if isinstance(pos, tuple):
            pos = self.mapToAbsPosition(*pos)
        
        endPos = pos + length
        
        if not self.document().findBlock(pos).isValid():
            raise IndexError('Invalid start position %d' % pos)
        
        if not self.document().findBlock(endPos).isValid():
            raise IndexError('Invalid end position %d' % endPos)
        
        cursor = QTextCursor(self.document())
        cursor.setPosition(pos)
        cursor.setPosition(endPos, QTextCursor.KeepAnchor)
        
        cursor.insertText(text)
    
    def insertText(self, pos, text):
        """Insert text at position
        
        If ``pos`` is an integer, it is interpreted as absolute position, if a tuple - as ``(line, column)``
        """
        return self.replaceText(pos, 0, text)
    
    def detectSyntax(self, xmlFileName = None, mimeType = None, language = None, sourceFilePath = None):
        """Get syntax by one of parameters:
        
            * xmlFileName
            * mimeType
            * language
            * sourceFilePath
        First parameter in the list has the hightest priority.
        Old syntax is always cleared, even if failed to detect new.
        
        Method returns ``True``, if syntax is detected, and ``False`` otherwise
        """
        oldLanguage = self.language()
        
        self.clearSyntax()
        
        syntax = self._globalSyntaxManager.getSyntax(SyntaxHighlighter.formatConverterFunction,
                                                     xmlFileName = xmlFileName,
                                                     mimeType = mimeType,
                                                     languageName = language,
                                                     sourceFilePath = sourceFilePath)

        if syntax is not None:
            self._highlighter = SyntaxHighlighter(syntax, self.document())
            self._indenter = self._getIndenter(syntax)
        
        newLanguage = self.language()
        if oldLanguage != newLanguage:
            self.languageChanged.emit(newLanguage)

    def clearSyntax(self):
        """Clear syntax. Disables syntax highlighting
        
        This method might take long time, if document is big. Don't call it if you don't have to (i.e. in destructor)
        """
        if self._highlighter is not None:
            self._highlighter.del_()
            self._highlighter = None
            self.languageChanged.emit(None)
    
    def language(self):
        """Get current language name.
        Return ``None`` for plain text
        """
        if self._highlighter is None:
            return None
        else:
            return self._highlighter.syntax().name
    
    def isCode(self, line, column):
        """Check if text at given position is a code
        If language is not known, or text is not parsed yet, True is returned
        """
        return self._highlighter is None or \
               self._highlighter.isCode(self.document().findBlockByNumber(line), column)

    def isComment(self, line, column):
        """Check if text at given position is a comment
        If language is not known, or text is not parsed yet, False is returned
        """
        return self._highlighter is not None and \
               self._highlighter.isComment(self.document().findBlockByNumber(line), column)

    def setExtraSelections(self, selections):
        """Set list of extra selections.
        Selections are list of tuples ``(startAbsolutePosition, length)``.
        Extra selections are reset on any text modification.
        
        This is reimplemented method of QPlainTextEdit, it has different signature. Do not use QPlainTextEdit method
        """
        def _makeQtExtraSelection(startAbsolutePosition, length):
            selection = QTextEdit.ExtraSelection()
            cursor = QTextCursor(self.document())
            cursor.setPosition(startAbsolutePosition)
            cursor.setPosition(startAbsolutePosition + length, QTextCursor.KeepAnchor)
            selection.cursor = cursor
            selection.format = self._userExtraSelectionFormat
            return selection
        
        self._userExtraSelections = [_makeQtExtraSelection(*item) for item in selections]
        self._updateExtraSelections()
    
    def mapToAbsPosition(self, line, column):
        """Convert line and column number to absolute position
        """
        block = self.document().findBlockByNumber(line)
        if not block.isValid():
            raise IndexError("Invalid line index %d" % line)
        if column >= block.length():
            raise IndexError("Invalid column index %d" % column)
        return block.position() + column
    
    def mapToLineCol(self, absPosition):
        """Convert absolute position to (line, column)
        """
        block = self.document().findBlock(absPosition)
        if not block.isValid():
            raise IndexError("Invalid absolute position %d" % absPosition)
        
        return (block.blockNumber(),
                absPosition - block.position())
    
    def _getIndenter(self, syntax):
        """Get indenter for syntax
        """
        if syntax.indenter is not None:
            try:
                return getIndenter(syntax.indenter, self)
            except KeyError:
                logger.error("Indenter '%s' not found" % syntax.indenter)
        
        try:
            return getIndenter(syntax.name, self)
        except KeyError:
            pass
        
        return getIndenter('normal', self)

    def _updateLineNumberAreaWidth(self, newBlockCount):
        """Set line number are width according to current lines count
        """
        self.setViewportMargins(self._lineNumberArea.width() + self._markArea.width(), 0, 0, 0)

    def _updateSideAreas(self, rect, dy):
        """Repaint line number area if necessary
        """
        # _countCache magic taken from Qt docs Code Editor Example
        if dy:
            self._lineNumberArea.scroll(0, dy)
            self._markArea.scroll(0, dy)
        elif self._countCache[0] != self.blockCount() or \
             self._countCache[1] != self.textCursor().block().lineCount():
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
            self._lineNumberArea.update(0, rect.y(), self._markArea.width(), rect.height())
        self._countCache = (self.blockCount(), self.textCursor().block().lineCount())

        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        pass # suppress dockstring for non-public method
        """QWidget.resizeEvent() implementation.
        Adjust line number area
        """
        QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self._lineNumberArea.width(), cr.height()))
        
        self._markArea.setGeometry(QRect(cr.left() + self._lineNumberArea.width(),
                                         cr.top(),
                                         self._markArea.width(),
                                         cr.height()))

    def _autoIndentBlock(self, block, char = '\n'):
        """Indent block after Enter pressed or trigger character typed
        """
        cursor = QTextCursor(block)
        currentText = block.text()
        spaceAtStartLen = len(currentText) - len(currentText.lstrip())
        currentIndent = currentText[:spaceAtStartLen]
        indent = self._indenter.computeIndent(block, char)
        if indent is not None and indent != currentIndent:
            self.replaceText(block.position(), spaceAtStartLen, indent)

    def _insertNewBlock(self):
        """Enter pressed.
        Insert properly indented block
        """
        cursor = self.textCursor()
        with self:
            cursor.insertBlock()
            self._autoIndentBlock(cursor.block())
        self.ensureCursorVisible()

    def _textBeforeCursor(self):
        """Text in current block from start to cursor position
        """
        cursor = self.textCursor()
        return cursor.block().text()[:cursor.positionInBlock()]

    def keyPressEvent(self, event):
        pass # suppress dockstring for non-public method
        """QPlainTextEdit.keyPressEvent() implementation.
        Catch events, which may not be catched with QShortcut and call slots
        """
        def _shouldUnindentWithBackspace():
            cursor = self.textCursor()
            text = cursor.block().text()
            spaceAtStartLen = len(text) - len(text.lstrip())
            
            return self._textBeforeCursor().endswith(self._indentText()) and \
                   not self.textCursor().hasSelection() and \
                   cursor.positionInBlock() == spaceAtStartLen
        
        def _shouldAutoIndent(event):
            cursor = self.textCursor()
            atEnd = cursor.positionInBlock() == cursor.block().length() - 1
            return atEnd and \
                   event.text() and \
                   event.text() in self._indenter.TRIGGER_CHARACTERS
        
        if event.matches(QKeySequence.InsertParagraphSeparator):
            self._insertNewBlock()
        elif event.key() == Qt.Key_Tab and event.modifiers() == Qt.NoModifier:
            if self.textCursor().hasSelection():
                self._onShortcutChangeSelectedBlocksIndentation(increase = True)
            else:
                self._onShortcutIndentAfterCursor()
        elif event.key() == Qt.Key_Backspace and \
             _shouldUnindentWithBackspace():
            self._onShortcutUnindentWithBackspace()
        elif event.matches(QKeySequence.MoveToStartOfLine):
            self._onShortcutHome(select=False)
        elif event.matches(QKeySequence.SelectStartOfLine):
            self._onShortcutHome(select=True)
        else:
            if _shouldAutoIndent(event):
                with self:
                    super(Qutepart, self).keyPressEvent(event)
                    self._autoIndentBlock(self.textCursor().block(), event.text())
            else:
                super(Qutepart, self).keyPressEvent(event)
    
    def _drawIndentMarkers(self, paintEventRect):
        """Draw indentation markers
        """
        painter = QPainter(self.viewport())
        painter.setPen(Qt.blue)
        
        indentWidthChars = len(self._indentText())
        indentWidthPixels = self.fontMetrics().width(' ' * self._indentWidth)
        
        cursorHeight = self.cursorRect().height()  # block might be wrapped,
                                                   # but we always draw marker, equal to single line width
        
        leftMargin = 7  # FIXME experimental value. Probably won't work on all themes and Qt versions
        
        for block in iterateBlocksFrom(self.firstVisibleBlock()):
            blockGeometry = self.blockBoundingGeometry(block).translated(self.contentOffset())
            if blockGeometry.top() > paintEventRect.bottom():
                break
            
            if block.isVisible() and blockGeometry.toRect().intersects(paintEventRect):
                text = block.text()
                x = blockGeometry.left() + indentWidthPixels + leftMargin
                while text.startswith(self._indentText()) and \
                      len(text) > indentWidthChars and \
                      text[indentWidthChars].isspace():
                    painter.drawLine(x,
                                     blockGeometry.top(),
                                     x,
                                     blockGeometry.top() + cursorHeight)
                    text = text[indentWidthChars:]
                    x = x + indentWidthPixels
    
    def paintEvent(self, event):
        pass # suppress dockstring for non-public method
        """Paint event
        Draw indentation markers after main contents is drawn
        """
        super(Qutepart, self).paintEvent(event)
        self._drawIndentMarkers(event.rect())
    
    def _currentLineExtraSelection(self):
        """QTextEdit.ExtraSelection, which highlightes current line
        """
        selection = QTextEdit.ExtraSelection()

        lineColor = QColor('#ffff99')

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        
        return selection

    def _updateExtraSelections(self):
        """Highlight current line
        """
        currentLineSelection = self._currentLineExtraSelection()

        # TODO use positionInBlock when Qt 4.6 is not supported
        cursorColumnIndex = self.textCursor().positionInBlock()
        
        bracketSelections = self._bracketHighlighter.extraSelections(self.textCursor().block(),
                                                                     cursorColumnIndex)
        allSelections = [currentLineSelection] + bracketSelections + self._userExtraSelections
        QPlainTextEdit.setExtraSelections(self, allSelections)

    def _onShortcutScroll(self, down):
        """Ctrl+Up/Down pressed, scroll viewport
        """
        value = self.verticalScrollBar().value()
        if down:
            value += 1
        else:
            value -= 1
        self.verticalScrollBar().setValue(value)
    
    def _onShortcutSelectAndScroll(self, down):
        """Ctrl+Shift+Up/Down pressed.
        Select line and scroll viewport
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Down if down else QTextCursor.Up, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self._onShortcutScroll(down)

    def _indentBlock(self, block):
        """Increase indentation level
        """
        QTextCursor(block).insertText(self._indentText())
    
    def _unIndentBlock(self, block):
        """Increase indentation level
        """
        text = block.text()
        
        if self._indentUseTabs:
            if text.startswith('\t'):
                charsToRemove = 1
            else:
                spacesCount = len(text) - len(text.lstrip(' '))
                charsToRemove = min(spacesCount, self._indentWidth)
        else:  # spaces
            if text.startswith(self._indentText()):  # remove indent level
                charsToRemove = self._indentWidth
            elif text.startswith('\t'):  # remove 1 Tab
                charsToRemove = 1
            else:  # remove all spaces
                charsToRemove = len(text) - len(text.lstrip(' '))
        
        if charsToRemove:
            cursor = QTextCursor(block)
            cursor.setPosition(cursor.position() + charsToRemove, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
    
    def _onShortcutChangeSelectedBlocksIndentation(self, increase):
        """Tab pressed and few blocks are selected, or Shift+Tab pressed
        Insert or remove text from the beginning of blocks
        """
        
        cursor = self.textCursor()

        startBlock = self.document().findBlock(cursor.selectionStart())
        endBlock = self.document().findBlock(cursor.selectionEnd())
        
        indentFunc = self._indentBlock if increase else self._unIndentBlock

        if startBlock != endBlock:  # indent multiply lines
            stopBlock = endBlock.next()
            
            block = startBlock
            
            with self:
                while block != stopBlock:
                    indentFunc(block)
                    block = block.next()
            
            newCursor = QTextCursor(startBlock)
            newCursor.setPosition(endBlock.position() + len(endBlock.text()), QTextCursor.KeepAnchor)
            self.setTextCursor(newCursor)
        else:  # indent 1 line
            indentFunc(cursor.block())

    def _onShortcutIndentAfterCursor(self):
        """Tab pressed and no selection. Insert text after cursor
        """
        cursor = self.textCursor()
        if self._indentUseTabs:
            cursor.insertText('\t')
        else:  # indent to integer count of indents from line start
            charsToInsert = self._indentWidth - (len(self._textBeforeCursor()) % self._indentWidth)
            cursor.insertText(' ' * charsToInsert)
    
    def _onShortcutUnindentWithBackspace(self):
        """Backspace pressed, unindent
        """
        assert self._textBeforeCursor().endswith(self._indentText())
        
        charsToRemove = len(self._textBeforeCursor()) % len(self._indentText())
        if charsToRemove == 0:
            charsToRemove = len(self._indentText())
        
        cursor = self.textCursor()
        cursor.setPosition(cursor.position() - charsToRemove, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
    
    def _onShortcutHome(self, select):
        """Home pressed, move cursor to the line start or to the text start
        """
        cursor = self.textCursor()
        anchor = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor
        text = cursor.block().text()
        spaceAtStartLen = len(text) - len(text.lstrip())
        if cursor.positionInBlock() == spaceAtStartLen:  # if at start of text
            cursor.setPositionInBlock(0, anchor)
        else:
            cursor.setPositionInBlock(spaceAtStartLen, anchor)
        self.setTextCursor(cursor)
    
    def _selectLines(self, startBlockNumber, endBlockNumber):
        """Select whole lines
        """
        startBlock = self.document().findBlockByNumber(startBlockNumber)
        endBlock = self.document().findBlockByNumber(endBlockNumber)
        cursor = QTextCursor(startBlock)
        cursor.setPosition(endBlock.position(), QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
    
    def _selectedBlocks(self):
        """Return selected blocks and tuple (startBlock, endBlock)
        """
        cursor = self.textCursor()
        return self.document().findBlock(cursor.selectionStart()), \
               self.document().findBlock(cursor.selectionEnd())
    
    def _selectedBlockNumbers(self):
        """Return selected block numbers and tuple (startBlockNumber, endBlockNumber)
        """
        startBlock, endBlock = self._selectedBlocks()
        return startBlock.blockNumber(), endBlock.blockNumber()
    
    def _onShortcutMoveLine(self, down):
        """Move line up or down
        Actually, not a selected text, but next or previous block is moved
        TODO keep bookmarks when moving
        """
        startBlock, endBlock = self._selectedBlocks()
        
        startBlockNumber = startBlock.blockNumber()
        endBlockNumber = endBlock.blockNumber()
        
        def _moveBlock(block, newNumber):
            text = block.text()
            with self:
                del self.lines[block.blockNumber()]
                self.lines.insert(newNumber, text)
        
        if down:  # move next block up
            blockToMove = endBlock.next()
            if not blockToMove.isValid():
                return
            
            # if operaiton is UnDone, marks are located incorrectly
            self._bookmarks.clear(startBlock, endBlock.next())
            
            _moveBlock(blockToMove, startBlockNumber)
            
            self._selectLines(startBlockNumber + 1, endBlockNumber + 1)
        else:  # move previous block down
            blockToMove = startBlock.previous()
            if not blockToMove.isValid():
                return
            
            # if operaiton is UnDone, marks are located incorrectly
            self._bookmarks.clear(startBlock.previous(), endBlock)
            
            _moveBlock(blockToMove, endBlockNumber)
            
            self._selectLines(startBlockNumber - 1, endBlockNumber - 1)
        
        self._markArea.update()
    
    def _selectedLinesSlice(self):
        """Get slice of selected lines
        """
        startBlockNumber, endBlockNumber = self._selectedBlockNumbers()
        return slice(startBlockNumber, endBlockNumber + 1, 1)
    
    def _onShortcutDeleteLine(self):
        """Delete line(s) under cursor
        """
        del self.lines[self._selectedLinesSlice()]
    
    def _onShortcutCopyLine(self):
        """Copy selected lines to the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]
        text = self._eol.join(lines)
        QApplication.clipboard().setText(text)
        
    def _onShortcutPasteLine(self):
        """Paste lines from the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]
        text = QApplication.clipboard().text()
        if text:
            with self:
                if self.textCursor().hasSelection():
                    startBlockNumber, endBlockNumber = self._selectedBlockNumbers()
                    del self.lines[self._selectedLinesSlice()]
                    self.lines.insert(startBlockNumber, text)
                else:
                    line, col = self.cursorPosition
                    if col > 0:
                        line = line + 1
                    self.lines.insert(line, text)
    
    def _onShortcutCutLine(self):
        """Cut selected lines to the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]

        self._onShortcutCopyLine()
        self._onShortcutDeleteLine()

    def _onShortcutDuplicateLine(self):
        """Duplicate selected text or current line
        """
        cursor = self.textCursor()
        if cursor.hasSelection():  # duplicate selection
            text = cursor.selectedText()
            selectionStart, selectionEnd = cursor.selectionStart(), cursor.selectionEnd()
            cursor.setPosition(selectionEnd)
            cursor.insertText(text)
            # restore selection
            cursor.setPosition(selectionStart)
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        else:
            line = cursor.blockNumber()
            self.lines.insert(line + 1, self.lines[line])
            self.ensureCursorVisible()
        
        self._updateExtraSelections()  # newly inserted text might be highlighted as braces
    
    def _onShortcutAutoIndentSelection(self):
        """Indent current line or selected lines
        """
        cursor = self.textCursor()
        
        startBlock = self.document().findBlock(cursor.selectionStart())
        endBlock = self.document().findBlock(cursor.selectionEnd())

        if startBlock != endBlock:  # indent multiply lines
            stopBlock = endBlock.next()
            
            block = startBlock
            
            with self:
                while block != stopBlock:
                    self._autoIndentBlock(block, '')
                    block = block.next()
        else:  # indent 1 line
            self._autoIndentBlock(startBlock, '')


def iterateBlocksFrom(block):
    """Generator, which iterates QTextBlocks from block until the End of a document
    """
    while block.isValid():
        yield block
        block = block.next()

def iterateBlocksBackFrom(block):
    """Generator, which iterates QTextBlocks from block until the Start of a document
    """
    while block.isValid():
        yield block
        block = block.previous()
