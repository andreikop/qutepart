"""QSyntaxHighlighter implementation
Uses syntax_manager module for doing the job
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush, QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextBlockUserData


class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, data):
        QTextBlockUserData.__init__(self)
        self.data = data


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, syntax, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._syntax = syntax
        self._quteparserToQtFormat = {}
    
    def _makeQtFormat(self, format):
        qtFormat = QTextCharFormat()
        qtFormat.setForeground(QBrush(QColor(format.color)))
        qtFormat.setBackground(QBrush(QColor(format.background)))
        qtFormat.setFontItalic(format.italic)
        qtFormat.setFontWeight(QFont.Bold if format.bold else QFont.Normal)
        qtFormat.setFontUnderline(format.underline)
        qtFormat.setFontStrikeOut(format.strikeOut)
        return qtFormat
    
    def _getQtFormat(self, format):
        try:
            return self._quteparserToQtFormat[id(format)]
        except KeyError:
            qtFormat = self._makeQtFormat(format)
            self._quteparserToQtFormat[id(format)] = qtFormat
            return qtFormat

    def _setFormat(self, start, length, format):
        if format is None:
            return
        qtFormat = self._getQtFormat(format)
        self.setFormat(start, length, qtFormat)

    def highlightBlock(self, text):
        parseBlockResult = self._syntax.parseBlock(text, self._prevData())
        #self._syntax.parseAndPrintBlockTextualResults(text, self._prevData())
        currentPos = 0
        
        for highlitedSegment in parseBlockResult.highlightedSegments:
            self._setFormat(currentPos, highlitedSegment.length, highlitedSegment.format)
            currentPos += highlitedSegment.length
        
        self.setCurrentBlockUserData(_TextBlockUserData(parseBlockResult.lineData))

    def _prevData(self):
        prevBlock = self.currentBlock().previous()
        if prevBlock.isValid():
            dataObject = prevBlock.userData()
            if dataObject is not None:
                return dataObject.data
        return None
