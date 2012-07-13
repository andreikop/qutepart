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
        
        currentColumnIndex = 0
        while currentColumnIndex < len(text):
            for rule in currentContext.rules:
                
                # Skip if column doesn't match
                if rule.column is not None and \
                   not rule.column == currentColumnIndex:
                    continue
                
                # Try to find rule match
                count = rule.findMatch(text[currentColumnIndex:])
                if count is not None:
                    print 'match', rule
                    self.setFormat(currentColumnIndex, count, self._theme.getFormat(rule.formatName))
                    currentColumnIndex += count
                    break
            else:
                self.setFormat(currentColumnIndex, 1, self._theme.getFormat(currentContext.formatName))
                currentColumnIndex += 1

    def _prevData(self):
        return self.currentBlock().previous().userData()
