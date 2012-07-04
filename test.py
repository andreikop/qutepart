#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter, \
    QTextCharFormat, QTextBlockUserData


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self._red = QTextCharFormat()
        self._red.setForeground(Qt.red)
    
    def highlightBlock(self, text):
        inside = False
        """
        prevData = self._prevData()
        if prevData is not None:
            inside = prevData.inside
        """
        print 'enter', self.currentBlock().position()
        block = self.currentBlock().next()
        if block.isValid():
            self.rehighlightBlock(block)        
        print 'exit'
        return
        
        prevIndex = 0
        index = text.find("'")
        while index != -1:
            if not inside:
                inside = True
                self._rehighlightNext()
            else:
                #self.setFormat(prevIndex, index - prevIndex + 1, self._red)
                self._rehighlightPrev()
                inside = False
            prevIndex = index
            index = text.find("'", index + 1)
        """
        data = QTextBlockUserData()
        data.inside = inside
        self.setCurrentBlockUserData(data)
        """

    def _prevData(self):
        return self.currentBlock().previous().userData()
    
    def _rehighlightNext(self):
        block = self.currentBlock().next()
        if block.isValid():
            self.rehighlightBlock(block)
    
    def _rehighlightPrev(self):
        block = self.currentBlock().previous()
        if block.isValid():
            self.rehighlightBlock(block)        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    pte = QPlainTextEdit()
    pte.setPlainText("''\n")
    hl = SyntaxHighlighter(pte.document())
    pte.show()
    app.exec_()
