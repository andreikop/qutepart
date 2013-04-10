"""QSyntaxHighlighter implementation
Uses syntax module for doing the job
"""

import time

from PyQt4.QtCore import Qt, QObject, QTimer
from PyQt4.QtGui import QBrush, QColor, QFont, \
                        QTextBlockUserData, QTextCharFormat, QTextDocument, QTextLayout


class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, data):
        QTextBlockUserData.__init__(self)
        self.data = data


class SyntaxHighlighter(QObject):
    
    # when initially parsing text, it is better, if highlighted text is drawn without flickering
    _MAX_PARSING_TIME_BIG_CHANGE_SEC = 0.4
    # when user is typing text - response shall be quick
    _MAX_PARSING_TIME_SMALL_CHANGE_SEC = 0.02

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
        
        self._pendingBlock = None
        self._pendingAtLeastUntilBlock = None
        
        self._continueTimer = QTimer()
        self._continueTimer.setSingleShot(True)
        self._continueTimer.timeout.connect(self._onContinueHighlighting)
        
        document.contentsChange.connect(self._onContentsChange)
        self._highlighBlocks(self._document.firstBlock(), self._document.lastBlock(),
                             self._MAX_PARSING_TIME_BIG_CHANGE_SEC)
    
    def del_(self):
        self._document.contentsChange.disconnect(self._onContentsChange)
        self._continueTimer.stop()
        block = self._document.firstBlock()
        while block.isValid():
            block.layout().setAdditionalFormats([])
            block.setUserData(None)
            self._document.markContentsDirty(block.position(), block.length())
            block = block.next()

    def syntax(self):
        """Return own syntax
        """
        return self._syntax

    def isCode(self, block, column):
        """Check if character at column is a a code
        """
        dataObject = block.userData()
        data = dataObject.data if dataObject is not None else None
        return self._syntax.isCode(data, column)

    def isComment(self, block, column):
        """Check if character at column is a comment
        """
        dataObject = block.userData()
        data = dataObject.data if dataObject is not None else None
        return self._syntax.isComment(data, column)

    def isBlockComment(self, block, column):
        """Check if character at column is a block comment
        """
        dataObject = block.userData()
        data = dataObject.data if dataObject is not None else None
        return self._syntax.isBlockComment(data, column)

    def isHereDoc(self, block, column):
        """Check if character at column is a here document
        """
        dataObject = block.userData()
        data = dataObject.data if dataObject is not None else None
        return self._syntax.isHereDoc(data, column)

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

    @staticmethod
    def _lineData(block):
        dataObject = block.userData()
        if dataObject is not None:
            return dataObject.data
        else:
            return None
    
    def _onContentsChange(self, from_, charsRemoved, charsAdded):
        firstBlock = self._document.findBlock(from_)
        untilBlock = self._document.findBlock(from_ + charsAdded)
        
        if self._continueTimer.isActive():  # have not finished task.
            """ Intersect ranges. Might produce a lot of extra highlighting work
            More complicated algorithm might be invented later
            """
            if self._pendingBlock.blockNumber() < firstBlock.blockNumber():
                firstBlock = self._pendingBlock
            if self._pendingAtLeastUntilBlock.blockNumber() > untilBlock.blockNumber():
                untilBlock = self._pendingAtLeastUntilBlock
            
            self._continueTimer.stop()
        
        timeout = self._MAX_PARSING_TIME_BIG_CHANGE_SEC if charsAdded > 20 else \
                  self._MAX_PARSING_TIME_SMALL_CHANGE_SEC
        
        self._highlighBlocks(firstBlock, untilBlock, timeout)

    def _onContinueHighlighting(self):
        self._highlighBlocks(self._pendingBlock, self._pendingAtLeastUntilBlock,
                             self._MAX_PARSING_TIME_SMALL_CHANGE_SEC)

    def _highlighBlocks(self, fromBlock, atLeastUntilBlock, timeout):
        endTime = time.clock() + timeout

        block = fromBlock
        lineData = self._lineData(block.previous())
        
        while block.isValid() and block != atLeastUntilBlock:
            if time.clock() >= endTime:  # time is over, schedule parsing later and release event loop
                self._pendingBlock = block
                self._pendingAtLeastUntilBlock = atLeastUntilBlock
                self._continueTimer.start()
                return
            
            contextStack = lineData[0] if lineData is not None else None
            lineData, highlightedSegments = self._syntax.highlightBlock(block.text(), contextStack)
            if lineData is not None:
                block.setUserData(_TextBlockUserData(lineData))
            else:
                block.setUserData(None)
            
            self._applyHighlightedSegments(block, highlightedSegments)
            block = block.next()
        
        # reached atLeastUntilBlock, now parse next only while data changed
        prevLineData = self._lineData(block)
        while block.isValid():
            if time.clock() >= endTime:  # time is over, schedule parsing later and release event loop
                self._pendingBlock = block
                self._pendingAtLeastUntilBlock = atLeastUntilBlock
                self._continueTimer.start()
                return

            contextStack = lineData[0] if lineData is not None else None
            lineData, highlightedSegments = self._syntax.highlightBlock(block.text(), contextStack)
            if lineData is not None:
                block.setUserData(_TextBlockUserData(lineData))
            else:
                block.setUserData(None)
            
            self._applyHighlightedSegments(block, highlightedSegments)
            if prevLineData == lineData:
                break
            
            block = block.next()
            prevLineData = self._lineData(block)
        
        # sucessfully finished, reset pending tasks
        self._pendingBlock = None
        self._pendingAtLeastUntilBlock = None

    def _applyHighlightedSegments(self, block, highlightedSegments):
        ranges = []
        currentPos = 0
        for length, format in highlightedSegments:
            range = QTextLayout.FormatRange()
            range.format = format
            range.start = currentPos
            range.length = length
            ranges.append(range)
            currentPos += length
            
        block.layout().setAdditionalFormats(ranges)
        self._document.markContentsDirty(block.position(), block.length())
