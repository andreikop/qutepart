"""QSyntaxHighlighter implementation
Uses Syntax module for doing the job
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextBlockUserData

from ColorTheme import ColorTheme
from Syntax import Syntax

class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, quoteIsOpened):
        QTextBlockUserData.__init__(self)
        self.quoteIsOpened = quoteIsOpened


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, syntaxFileName, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._theme = ColorTheme()
        self._syntax = Syntax(syntaxFileName)
    
    def highlightBlock(self, text):
        print self._syntax.parseBlockTextualResults(text)
        contextAreaStartPos = 0
        for context, contextLength, matchedRules in self._syntax.parseBlock(text):
            self.setFormat(contextAreaStartPos, contextLength, self._theme.getFormat(context.formatName))
            for rule, pos, ruleLength in matchedRules:
                self.setFormat(contextAreaStartPos + pos, ruleLength, self._theme.getFormat(rule.formatName))
            contextAreaStartPos += contextLength

    def _prevData(self):
        return self.currentBlock().previous().userData()
