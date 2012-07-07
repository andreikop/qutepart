#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData

class _TextBlockUserData(QTextBlockUserData):
    def __init__(self, quoteIsOpened):
        QTextBlockUserData.__init__(self)
        self.quoteIsOpened = quoteIsOpened


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._red = QTextCharFormat()
        self._red.setForeground(Qt.red)
    
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
                self.setFormat(prevIndex, index - prevIndex + 1, self._red)
                quoteIsOpened = False
            prevIndex = index
            index = text.find("'", index + 1)
        if quoteIsOpened:
            self.setFormat(prevIndex, len(text) - prevIndex, self._red)
        
        self.setCurrentBlockUserData(_TextBlockUserData(quoteIsOpened))
        self.setCurrentBlockState(quoteIsOpened)

    def _prevData(self):
        return self.currentBlock().previous().userData()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText("''\n")
    hl = SyntaxHighlighter(pte.document())
    pte.show()
    app.exec_()
