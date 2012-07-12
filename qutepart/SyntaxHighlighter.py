from PyQt4.QtCore import Qt
from PyQt4.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextBlockUserData

from ColorTheme import ColorTheme
from Syntax import Syntax

class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, quoteIsOpened):
        QTextBlockUserData.__init__(self)
        self.quoteIsOpened = quoteIsOpened


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._theme = ColorTheme()
        self._syntax = Syntax('debianchangelog.xml')
    
    def highlightBlock(self, text):
        currentContext = self._syntax.defaultContext
        
        for characterIndex, character in enumerate(text):
            for rule in currentContext.rules:
                matchedIndex = rule.findMatch(text[characterIndex:])

    def _prevData(self):
        return self.currentBlock().previous().userData()
