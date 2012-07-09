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
        prevIndex = 0
        index = text.find("'")
        
        prevData = self._prevData()
        if prevData is not None:
            quoteIsOpened = prevData.quoteIsOpened
        else:
            quoteIsOpened = False

        while index != -1:
            if not quoteIsOpened:
                quoteIsOpened = True
            else:
                self.setFormat(prevIndex, index - prevIndex + 1, self._theme.getFormat('String'))
                quoteIsOpened = False
            prevIndex = index
            index = text.find("'", index + 1)
        if quoteIsOpened:
            self.setFormat(prevIndex, len(text) - prevIndex, self._theme.getFormat('String'))
        
        self.setCurrentBlockUserData(_TextBlockUserData(quoteIsOpened))
        self.setCurrentBlockState(quoteIsOpened)

    def _prevData(self):
        return self.currentBlock().previous().userData()
