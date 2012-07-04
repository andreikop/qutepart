#!/usr/bin/env python

import sys

import sip
sip.setapi('QString', 2)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPlainTextEdit, QSyntaxHighlighter


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
    
    def highlightBlock(self, text):
        block = self.currentBlock().next()
        if block.isValid():
            self.rehighlightBlock(block)        

app = QApplication(sys.argv)

pte = QPlainTextEdit()
pte.setPlainText("\n")
hl = SyntaxHighlighter(pte.document())
pte.show()
app.exec_()
