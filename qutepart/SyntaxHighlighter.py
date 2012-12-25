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
        
        self._parseAll()
        
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

    def _parseAll(self):
        syntax = self._syntax
        block = self._document.firstBlock()
        lineData = None
        while block.isValid():
            lineData = syntax.parseBlock(block.text(), lineData)
            block.setUserData(_TextBlockUserData(lineData))
            block = block.next()
    
    def _highlightAll(self):
        syntax = self._syntax
        block = self._document.firstBlock()
        lineData = None
        while block.isValid():
            lineData, highlightedSegments = syntax.highlightBlock(block.text(), lineData)
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

    def _prevData(self, block):
        prevBlock = block.previous()
        if prevBlock.isValid():
            dataObject = prevBlock.userData()
            if dataObject is not None:
                return dataObject.data
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
