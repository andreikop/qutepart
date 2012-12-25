"""QSyntaxHighlighter implementation
Uses syntax module for doing the job
"""

from PyQt4.QtCore import Qt, QObject
from PyQt4.QtGui import QBrush, QColor, QFont, \
                        QTextBlockUserData, QTextCharFormat, QTextDocument, QTextLayout


class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, data):
        QTextBlockUserData.__init__(self)
        self.data = data


class SyntaxHighlighter(QObject):
    @staticmethod
    def formatConverterFunction(format):
        qtFormat = QTextCharFormat()
        qtFormat.setForeground(QBrush(QColor(format.color)))
        qtFormat.setBackground(QBrush(QColor(format.background)))
        qtFormat.setFontItalic(format.italic)
        qtFormat.setFontWeight(QFont.Bold if format.bold else QFont.Normal)
        qtFormat.setFontUnderline(format.underline)
        qtFormat.setFontStrikeOut(format.strikeOut)

        return qtFormat

    def __init__(self, syntax, object):
        if isinstance(object, QTextDocument):
            document = object
        elif isinstance(object, QTextEdit):
            document = object.document()
            assert document is not None
        else:
            raise TypeError("object must be QTextDocument or QTextEdit")
        
        QObject.__init__(self, document)
        self._syntax = syntax
        self._document = document
        
        document.contentsChange.connect(self._onContentsChange)
        
        self._highlightAllInitial()

    def _parseAllInitial(self):
        syntax = self._syntax
        block = self._document.firstBlock()
        lineData = None
        while block.isValid():
            lineData = syntax.parseBlock(block.text(), lineData)
            if lineData is not None:
                block.setUserData(_TextBlockUserData(lineData))
            block = block.next()
    
    def _highlightAllInitial(self):
        syntax = self._syntax
        block = self._document.firstBlock()
        lineData = None
        while block.isValid():
            lineData, highlightedSegments = syntax.highlightBlock(block.text(), lineData)
            if lineData is not None:
                block.setUserData(_TextBlockUserData(lineData))
            self._applyHighlightedSegments(block, highlightedSegments)
            block = block.next()

    def _highlightBlock(self, block):
        if True:
            lineData, highlightedSegments = self._syntax.highlightBlock(block.text(), self._prevData(block))
            self._applyHighlightedSegments(block, highlightedSegments)
        else:
            lineData = self._syntax.parseBlock(text, self._prevData(block))

        block.setUserData(_TextBlockUserData(lineData))

    @staticmethod
    def _lineData(block):
        dataObject = block.userData()
        if dataObject is not None:
            return dataObject.data
        else:
            return None
    
    def _applyHighlightedSegments(self, block, highlightedSegments):
        layout = block.layout()
        ranges = []
        currentPos = 0
        for length, format in highlightedSegments:
            range = QTextLayout.FormatRange()
            range.format = format
            range.start = currentPos
            range.length = length
            ranges.append(range)
            currentPos += length
            
        layout.setAdditionalFormats(ranges)
        self._document.markContentsDirty(block.position(), block.length())

    def _onContentsChange(self, from_, charsRemoved, charsAdded):
        block = self._document.findBlock(from_)
        lastBlockNumber = self._document.findBlock(from_ + charsAdded).blockNumber()

        # unconditional parsing
        lineData = self._lineData(block.previous())
        for i in xrange(block.blockNumber(), lastBlockNumber - 1):
            lineData, highlightedSegments = self._syntax.highlightBlock(block.text(), lineData)
            block.setUserData(_TextBlockUserData(lineData))
            self._applyHighlightedSegments(block, highlightedSegments)
            block = block.next()

        # parse next only while data changed
        prevLineData = self._lineData(block)
        while block.isValid():
            lineData, highlightedSegments = self._syntax.highlightBlock(block.text(), lineData)
            if lineData is not None:
                block.setUserData(_TextBlockUserData(lineData))
            else:
                block.setUserData(None)
            self._applyHighlightedSegments(block, highlightedSegments)
            if prevLineData == lineData:
                break
            block = block.next()
            prevLineData = self._lineData(block)
