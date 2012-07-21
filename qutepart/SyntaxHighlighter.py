"""QSyntaxHighlighter implementation
Uses Syntax module for doing the job
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextBlockUserData

from ColorTheme import ColorTheme
from Syntax import Syntax

class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, data):
        QTextBlockUserData.__init__(self)
        self.data = data


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, syntaxFileName, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._theme = ColorTheme()
        self._syntax = Syntax(syntaxFileName)
    
    def highlightBlock(self, text):
        lineData, matchedContexts = self._syntax.parseBlock(text, self._prevData())
        print self._syntax.parseBlockTextualResults(text, self._prevData())
        contextAreaStartPos = 0
        for context, contextLength, matchedRules in matchedContexts:
            self.setFormat(contextAreaStartPos, contextLength, self._theme.getFormat(context.mappedAttribute))
            for rule, pos, ruleLength in matchedRules:
                if rule.mappedAttribute is not None:
                    self.setFormat(pos, ruleLength, self._theme.getFormat(rule.mappedAttribute))
            contextAreaStartPos += contextLength
        
        self.setCurrentBlockUserData(_TextBlockUserData(lineData))

    def _prevData(self):
        prevBlock = self.currentBlock().previous()
        if prevBlock.isValid():
            dataObject = prevBlock.userData()
            if dataObject is not None:
                return dataObject.data
        return None
