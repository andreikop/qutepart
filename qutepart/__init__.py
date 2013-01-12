"""Code editor component for PyQt and Pyside

Use Qutepart class as an API
"""

import os.path

from PyQt4.QtCore import QRect, Qt
from PyQt4.QtGui import QColor, QFont, QKeySequence, QPainter, QPlainTextEdit, \
                        QPixmap, QTextEdit, QTextFormat, QWidget

from qutepart.syntax import SyntaxManager
from qutepart.syntaxhlighter import SyntaxHighlighter
from qutepart.brackethlighter import BracketHighlighter
from qutepart.indenter import getIndenter
from qutepart.completer import Completer


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
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self._qpart.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset()).top())
        bottom = top + int(self._qpart.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
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
        
        defaultSizePixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'icons', 'bookmark.png'))
        iconSize = self._qpart.cursorRect().height()
        self._bookmarkPixmap = defaultSizePixmap.scaled(iconSize, iconSize)
    
    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self._qpart.firstVisibleBlock()
        top = int(self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset()).top())
        bottom = top + int(self._qpart.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawPixmap(0, top, self._bookmarkPixmap)
            
            top += int(self._qpart.blockBoundingRect(block).height())
            block = block.next()

    def width(self):
        """Desired width. Includes text and margins
        """
        return self._MARGIN + self._bookmarkPixmap.width() + self._MARGIN


class Qutepart(QPlainTextEdit):
    """Code editor component for PyQt and Pyside
    """
    
    _DEFAULT_INDENTATION = '    '
    
    _globalSyntaxManager = SyntaxManager()
    
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        self.setFont(QFont("Monospace"))
        
        self._highlighter = None
        self._bracketHighlighter = BracketHighlighter()
        
        self._indenter = getIndenter('normal', self._DEFAULT_INDENTATION)
        
        self._completer = Completer(self)
        
        self._lineNumberArea = _LineNumberArea(self)
        self._countCache = (-1, -1)
        self._markArea = _MarkArea(self)

        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateLineNumberArea)
        self.cursorPositionChanged.connect(self._updatePositionHighlighting)

        self._updateLineNumberAreaWidth(0)
        self._updatePositionHighlighting()
    
    def detectSyntax(self, xmlFileName = None, mimeType = None, languageName = None, sourceFilePath = None):
        """Get syntax by one of parameters:
            * xmlFileName
            * mimeType
            * languageName
            * sourceFilePath
        First parameter in the list has biggest priority.
        Old syntax is always cleared, even if failed to detect new.
        
        Method returns True, if syntax is detected, and False otherwise
        """
        self.clearSyntax()
        
        syntax = self._globalSyntaxManager.getSyntax(SyntaxHighlighter.formatConverterFunction,
                                                     xmlFileName = xmlFileName,
                                                     mimeType = mimeType,
                                                     languageName = languageName,
                                                     sourceFilePath = sourceFilePath)

        if syntax is not None:
            self._highlighter = SyntaxHighlighter(syntax, self.document())
            self._indenter = self._getIndenter(syntax)

    def _getIndenter(self, syntax):
        """Get indenter for syntax
        """
        if syntax.indenter is not None:
            try:
                return getIndenter(syntax.indenter, self._DEFAULT_INDENTATION)
            except KeyError:
                print >> sys.stderr, "Indenter '%s' not found" % syntax.indenter
        
        try:
            return getIndenter(syntax.name, self._DEFAULT_INDENTATION)
        except KeyError:
            pass
        
        return getIndenter('normal', self._DEFAULT_INDENTATION)

    def clearSyntax(self):
        """Clear syntax. Disables syntax highlighting
        
        This method might take long time, if document is big. Don't call it if you don't have to.
        """
        if self._highlighter is not None:
            self._highlighter.del_()
            self._highlighter = None
    
    def languageName(self):
        """Get current language name
        Return None for plain text
        """
        if self._highlighter is None:
            return None
        else:
            return self._highlighter.syntax().name
    
    def _updateLineNumberAreaWidth(self, newBlockCount):
        """Set line number are width according to current lines count
        """
        self.setViewportMargins(self._lineNumberArea.width() + self._markArea.width(), 0, 0, 0)

    def _updateLineNumberArea(self, rect, dy):
        """Repaint line number area if necessary
        """
        # _countCache magic taken from Qt docs Code Editor Example
        if dy:
            self._lineNumberArea.scroll(0, dy)
        elif self._countCache[0] != self.blockCount() or \
             self._countCache[1] != self.textCursor().block().lineCount():
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        self._countCache = (self.blockCount(), self.textCursor().block().lineCount())

        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
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

    def keyPressEvent(self, event):
        """QPlainTextEdit.keyPressEvent() implementation.
        Autoindents text if new line inserted
        """
        if event.matches(QKeySequence.InsertParagraphSeparator):
            self._insertNewBlock()
        else:
            super(Qutepart, self).keyPressEvent(event)

    def _insertNewBlock(self):
        """Enter pressed.
        Insert properly indented block
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        try:
            cursor.insertBlock()
            indent = self._indenter.computeIndent(self.textCursor().block())
            cursor.insertText(indent)
        finally:
            cursor.endEditBlock()

    def _currentLineExtraSelection(self):
        """QTextEdit.ExtraSelection, which highlightes current line
        """
        selection = QTextEdit.ExtraSelection()

        lineColor = QColor(Qt.yellow).lighter(160)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        
        return selection

    def _updatePositionHighlighting(self):
        """Highlight current line
        """
        currentLineSelection = self._currentLineExtraSelection()

        # TODO use positionInBlock when Qt 4.6 is not supported
        cursorColumnIndex = self.textCursor().position() - self.textCursor().block().position()
        
        bracketSelections = self._bracketHighlighter.extraSelections(self.textCursor().block(),
                                                                     cursorColumnIndex)
        self.setExtraSelections([currentLineSelection] + bracketSelections)
