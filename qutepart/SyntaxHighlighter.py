"""QSyntaxHighlighter implementation
Uses Syntax module for doing the job
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
    
    def _makeQtFormat(self, format):
        qtFormat = QTextCharFormat()
        qtFormat.setForeground(QBrush(QColor(format.color)))
        qtFormat.setBackground(QBrush(QColor(format.background)))
        qtFormat.setFontItalic(format.italic)
        qtFormat.setFontWeight(QFont.Bold if format.bold else QFont.Normal)
        qtFormat.setFontUnderline(format.underline)
        qtFormat.setFontStrikeOut(format.strikeOut)
        return qtFormat

    def _setFormat(self, start, length, format):
        qtFormat = self._makeQtFormat(format)
        self.setFormat(start, length, qtFormat)

    def highlightBlock(self, text):
        parseBlockResult = self._syntax.parseBlock(text, self._prevData())
        #self._syntax.parseAndPrintBlockTextualResults(text, self._prevData())
        contextAreaStartPos = 0
        
        for matchedContext in parseBlockResult.matchedContexts:
            self._setFormat(contextAreaStartPos, matchedContext.length, matchedContext.context.format)
            for matchedRule in matchedContext.matchedRules:
                if matchedRule.rule.attribute is not None:
                    self._setFormat(matchedRule.pos, matchedRule.length, matchedRule.rule.format)
            contextAreaStartPos += matchedContext.length
        
        self.setCurrentBlockUserData(_TextBlockUserData(parseBlockResult.lineData))

    def _prevData(self):
        prevBlock = self.currentBlock().previous()
        if prevBlock.isValid():
            dataObject = prevBlock.userData()
            if dataObject is not None:
                return dataObject.data
        return None
